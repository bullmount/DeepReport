import asyncio
import concurrent.futures
import signal
import sys
import threading
import time
import traceback
from typing import Any, Optional, Callable, Dict, List

from langchain_core.runnables import RunnableConfig


class GraphRunningState:
    """Classe che rappresenta lo stato di esecuzione del grafo"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ABORTED = "aborted"
    ERROR = "error"
    TIMEOUT = "timeout"  # Stato specifico per timeout


class LangGraphRunner:
    """
    Runner per l'esecuzione controllata di grafi LangGraph, con supporto per:
    - Esecuzione sincrona con timeout
    - Esecuzione asincrona con possibilità di abort forzato
    - Callback per eventi e progresso
    """

    def __init__(self):
        """Inizializza il runner."""
        self._executor = None
        self._future = None
        self._worker_thread = None  # Thread di lavoro dedicato
        self._should_abort = False
        self._abort_event = threading.Event()
        self._state = GraphRunningState.IDLE
        self._current_state = None
        self._error = None
        self._on_event_callback = None
        self._on_state_change_callback = None
        self._on_completion_callback = None
        self._on_abort_callback = None
        self._on_error_callback = None
        self._on_timeout_callback = None
        self._executor_lock = threading.RLock()  # Lock per le operazioni sull'executor

    def register_event_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Registra un callback per gli eventi del grafo"""
        self._on_event_callback = callback

    def register_state_change_callback(self, callback: Callable[[str, Any], None]):
        """Registra un callback per i cambiamenti di stato dell'esecuzione"""
        if self._state != GraphRunningState.ABORTED:
            self._on_state_change_callback = callback

    def register_completion_callback(self, callback: Callable[[Any], None]):
        """Registra un callback per il completamento dell'esecuzione"""
        if self._state != GraphRunningState.ABORTED:
            self._on_completion_callback = callback

    def register_abort_callback(self, callback: Callable[[], None]):
        """Registra un callback per l'abort dell'esecuzione"""
        self._on_abort_callback = callback

    def register_error_callback(self, callback: Callable[[Exception], None]):
        """Registra un callback per gli errori durante l'esecuzione"""
        self._on_error_callback = callback

    def register_timeout_callback(self, callback: Callable[[], None]):
        """Registra un callback per gli eventi di timeout"""
        if self._state != GraphRunningState.ABORTED:
            self._on_timeout_callback = callback

    def _set_state(self, new_state: str):
        """Imposta lo stato interno e notifica il callback se registrato"""
        old_state = self._state
        self._state = new_state
        if self._on_state_change_callback and old_state != new_state:
            try:
                self._on_state_change_callback(new_state, self._current_state)
            except Exception as e:
                print(f"Errore nel callback di cambio stato: {e}")

    def _notify_event(self, event: Dict[str, Any]):
        """Notifica un evento al callback registrato"""
        if self._on_event_callback:
            try:
                self._on_event_callback(event)
            except Exception as e:
                print(f"Errore nel callback di evento: {e}")

    def _force_exit_thread(self):
        """Forza l'uscita del thread di lavoro"""
        if self._worker_thread and self._worker_thread.is_alive():
            thread_id = self._worker_thread.ident

            # Metodo 1: Usa pthread_kill su sistemi Linux/Mac
            if hasattr(signal, 'pthread_kill') and thread_id:
                try:
                    signal.pthread_kill(thread_id, signal.SIGINT)
                    print(f"Signal SIGINT sent to thread {thread_id}")
                except Exception as e:
                    print(f"Error sending pthread_kill: {e}")

            # Metodo 2: Usa metodi platform-specific
            if sys.platform == 'win32':
                # Su Windows non abbiamo pthread_kill, quindi usiamo altre strategie
                try:
                    # Tenta di terminare il thread tramite il suo executor
                    with self._executor_lock:
                        if self._executor and not getattr(self._executor, "_shutdown", False):
                            self._executor.shutdown(wait=False, cancel_futures=True)
                            print("Executor shutdown with cancel_futures=True")
                except Exception as e:
                    print(f"Error shutting down executor: {e}")

            # Metodo 3: Usa una variabile di controllo che il thread deve controllare regolarmente
            self._abort_event.set()
            self._should_abort = True

            # Attendi brevemente per vedere se il thread termina
            waited = 0
            while self._worker_thread.is_alive() and waited < 5:  # timeout di 5 secondi
                time.sleep(0.2)
                waited += 0.2

            if self._worker_thread.is_alive():
                print(f"Warning: Thread {thread_id} still running after abort")
                # Nota: non possiamo terminare forzatamente un thread in Python,
                # ma l'executor dovrebbe aver cancellato le future

    def _check_abort(self):
        """Verifica periodicamente il flag di abort in un thread separato"""
        try:
            while not self._abort_event.is_set():
                if self._should_abort:
                    print("Abort flag detected in monitor thread")
                    self._abort_event.set()
                    self._force_exit_thread()
                    break
                time.sleep(0.2)  # controlla più frequentemente
            print("Abort monitor thread exiting")
        except Exception as e:
            print(f"Error in abort monitor thread: {e}")
            traceback.print_exc()

    def _execute_graph(self, chain, initial_state: Any, config: Optional[RunnableConfig] = None):
        """Esecuzione del grafo in un thread dedicato con gestione degli eventi e dell'abort"""
        try:
            self._set_state(GraphRunningState.RUNNING)
            self._current_state = initial_state
            current_input = initial_state

            # Salva il riferimento al thread corrente per permettere l'abort forzato
            self._worker_thread = threading.current_thread()

            # Avvia un thread separato per il controllo dell'abort
            abort_checker = threading.Thread(target=self._check_abort)
            abort_checker.daemon = True
            abort_checker.start()

            try:
                while not self._abort_event.is_set():
                    any_event_processed = False

                    try:
                        for event in chain.stream(current_input, config, stream_mode="updates"):
                            any_event_processed = True
                            self._notify_event(event)

                            if self._abort_event.is_set():
                                print("Abort event detected during event processing")
                                raise KeyboardInterrupt("Operation aborted by user")

                            if '__interrupt__' in event:
                                interrupt_value = event['__interrupt__'][0].value
                                # Gestiamo l'interruzione in modo non-bloccante
                                self._current_state = interrupt_value
                                # Attendiamo la risposta
                                wait_start = time.time()
                                while not self._abort_event.is_set():
                                    if hasattr(self, '_user_response') and self._user_response is not None:
                                        current_input = self._user_response
                                        delattr(self, '_user_response')
                                        break

                                    # Controlliamo se è passato troppo tempo
                                    # if time.time() - wait_start > 30:  # timeout di 30 secondi per input utente
                                    #     break

                                    time.sleep(0.1)

                        # Aggiorna lo stato corrente
                        graph_state = chain.get_state(config)
                        self._current_state = graph_state.values

                        # Controlla se il grafo è terminato
                        if graph_state.next == ():
                            break

                    except Exception as e:
                        if self._abort_event.is_set():
                            print(f"Expected exception during abort: {e}")
                            raise KeyboardInterrupt("Operation aborted by user")
                        else:
                            print(f"Unexpected exception during graph execution: {e}")
                            traceback.print_exc()
                            raise

                    # Se non abbiamo processato eventi in questo ciclo, aggiungiamo
                    # un breve sleep per evitare di sovraccaricare la CPU
                    if not any_event_processed:
                        time.sleep(0.1)

                        # Controlliamo periodicamente il flag di abort
                        if self._abort_event.is_set():
                            print("Abort event detected during idle time")
                            raise KeyboardInterrupt("Operation aborted by user")

                # Esecuzione completata con successo
                if not self._abort_event.is_set():
                    print("Graph execution completed successfully")
                    self._set_state(GraphRunningState.COMPLETED)

                    if self._on_completion_callback:
                        try:
                            self._on_completion_callback(self._current_state)
                        except Exception as e:
                            print(f"Error in completion callback: {e}")

                return self._current_state

            except KeyboardInterrupt:
                print("KeyboardInterrupt caught in execute_graph")
                if self._state == GraphRunningState.TIMEOUT:
                    print("Execution timed out")
                    if self._on_timeout_callback:
                        try:
                            self._on_timeout_callback()
                        except Exception as e:
                            print(f"Error in timeout callback: {e}")
                else:
                    self._set_state(GraphRunningState.ABORTED)
                    print("Execution aborted by user")
                    if self._on_abort_callback:
                        try:
                            self._on_abort_callback()
                        except Exception as e:
                            print(f"Error in abort callback: {e}")

                # Restituisci lo stato parziale
                return self._current_state

        except Exception as e:
            print(f"Error in execute_graph: {e}")
            traceback.print_exc()
            self._error = e
            self._set_state(GraphRunningState.ERROR)

            if self._on_error_callback:
                try:
                    self._on_error_callback(e)
                except Exception as callback_e:
                    print(f"Error in error callback: {callback_e}")

            raise e

        finally:
            print("Cleaning up in execute_graph finally block")
            self._should_abort = False
            # Chiudi l'executor in sicurezza
            self._cleanup_executor()

    def _cleanup_executor(self):
        """Pulisce l'executor in modo sicuro"""
        with self._executor_lock:
            if self._executor and not getattr(self._executor, "_shutdown", False):
                try:
                    print("Waiting 3 seconds before shutdown...")
                    # Prima attendi 3 secondi per permettere ai task di completarsi
                    time.sleep(3)
                    print("Shutting down executor")
                    self._executor.shutdown(wait=False)
                except Exception as e:
                    print(f"Error in executor shutdown: {e}")
                finally:
                    self._executor = None

    def run(self, chain, initial_state: Any, config: Optional[RunnableConfig] = None,
            timeout: Optional[float] = None, blocking: bool = True) -> Any:
        """
        Esegue il grafo in modo sincrono o asincrono

        Args:
            chain: Il grafo compilato da eseguire
            initial_state: Lo stato iniziale per l'esecuzione
            config: Configurazione opzionale per il runnable
            timeout: Timeout in secondi (None per nessun timeout)
            blocking: Se True, attende il completamento, altrimenti ritorna subito

        Returns:
            Il risultato dell'esecuzione o None se non-blocking
        """
        # Reset dello stato
        self._should_abort = False
        self._abort_event.clear()
        self._set_state(GraphRunningState.IDLE)
        self._error = None
        self._current_state = initial_state

        # Pulisci eventuali executor precedenti
        self._cleanup_executor()

        # Crea un nuovo executor per gestire il task
        with self._executor_lock:
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            # Avvia l'esecuzione in un thread separato
            self._future = self._executor.submit(self._execute_graph, chain, initial_state, config)

        # Se non è bloccante, ritorna subito
        if not blocking:
            return None

        # Attendi il risultato con timeout opzionale
        try:
            if timeout is not None:
                print(f"Waiting for result with timeout {timeout} seconds")
                result = self._future.result(timeout=timeout)
                print("Result received before timeout")
                return result
            else:
                print("Waiting for result without timeout")
                result = self._future.result()
                print("Result received")
                return result

        except concurrent.futures.TimeoutError:
            print(f"Timeout occurred after {timeout} seconds")
            # Imposta lo stato di timeout e forza l'interruzione
            self._set_state(GraphRunningState.TIMEOUT)
            # Segnala l'abort con modalità forzata
            self._should_abort = True
            self._abort_event.set()
            # Forza l'uscita dal thread
            self._force_exit_thread()
            # Notifica il timeout
            if self._on_timeout_callback:
                try:
                    self._on_timeout_callback()
                except Exception as e:
                    print(f"Error in timeout callback: {e}")

            return self._current_state

        except Exception as e:
            print(f"Error during run: {e}")
            traceback.print_exc()
            # Gestisci eventuali altre eccezioni
            if self._state not in [GraphRunningState.ERROR, GraphRunningState.ABORTED, GraphRunningState.TIMEOUT]:
                self._error = e
                self._set_state(GraphRunningState.ERROR)
                if self._on_error_callback:
                    try:
                        self._on_error_callback(e)
                    except Exception as callback_e:
                        print(f"Error in error callback: {callback_e}")

            # Assicura che l'esecuzione venga interrotta
            if not self._abort_event.is_set():
                self._should_abort = True
                self._abort_event.set()
                self._force_exit_thread()

            return self._current_state

    def provide_user_response(self, response: Any):
        """
        Fornisce una risposta utente quando il grafo è in attesa di input

        Args:
            response: La risposta dell'utente
        """
        if self._state == GraphRunningState.RUNNING:
            self._user_response = response

    def abort(self) -> bool:
        """
        Forza l'interruzione dell'esecuzione del grafo

        Returns:
            True se l'abort è stato richiesto, False se il grafo non è in esecuzione
        """
        if self._state == GraphRunningState.RUNNING:
            print("Abort requested by user")
            self._should_abort = True
            self._abort_event.set()
            self._force_exit_thread()
            self._set_state(GraphRunningState.ABORTED)
            return True
        return False

    def get_state(self) -> str:
        """
        Restituisce lo stato attuale dell'esecuzione

        Returns:
            Lo stato di esecuzione corrente
        """
        return self._state

    def is_running(self) -> bool:
        """
        Controlla se il grafo è in esecuzione

        Returns:
            True se il grafo è in esecuzione, False altrimenti
        """
        return self._state == GraphRunningState.RUNNING

    def get_result(self, timeout: Optional[float] = None) -> Any:
        """
        Ottiene il risultato dell'esecuzione, aspettando se necessario

        Args:
            timeout: Timeout in secondi (None per attendere indefinitamente)

        Returns:
            Il risultato dell'esecuzione o None in caso di timeout
        """
        if self._future and not self._future.done():
            try:
                if timeout is not None:
                    print(f"get_result waiting with timeout {timeout} seconds")
                else:
                    print("get_result waiting without timeout")

                result = self._future.result(timeout=timeout)
                print("get_result received result")
                return result

            except concurrent.futures.TimeoutError:
                print(f"get_result timeout occurred after {timeout} seconds")
                # Non facciamo abort qui, restituiamo semplicemente lo stato corrente
                return self._current_state

            except Exception as e:
                print(f"Error in get_result: {e}")
                traceback.print_exc()
                return self._current_state

        print("get_result returning current state (future is done or None)")
        return self._current_state

    def get_current_state(self) -> Any:
        """
        Ottiene lo stato corrente dell'esecuzione

        Returns:
            Lo stato corrente del grafo
        """
        return self._current_state

    def get_error(self) -> Optional[Exception]:
        """
        Ottiene l'errore verificatosi durante l'esecuzione, se presente

        Returns:
            L'eccezione verificatasi o None
        """
        return self._error