import time
from typing import List

from langgraph.graph import END, StateGraph, START
from langchain_core.runnables import RunnableConfig
from agents import ReportPlannerAgent
from agents.agent_base import DeepReportAgentBase, EventData
from agents.build_section_with_web_research import BuildSectionWithWebResearch
from agents.compile_final_report import CompileFinalReport
from agents.gather_completed_sections_agent import GatherCompletedSections
from agents.human_feedback_agent import HumanFeedbackAgent
from agents.write_final_sections_agent import WriteFinalSectionsAgent

from configuration import Configuration, SearchAPI
from deep_report_state import (DeepReportState, DeepReportStateInput, DeepReportStateOutput,
                               SectionState, SectionOutputState)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, Send

from event_notifier import ProcessState
from utils.lang_graph_runner import LangGraphRunner


class ChiefDeepReportAgent(DeepReportAgentBase):
    def __init__(self,
                 number_of_queries: int = 2,
                 max_results_per_query: int = 4,
                 max_search_depth: int = 2,
                 search_api: SearchAPI = SearchAPI.GOOGLESEARCH,
                 domains_search_restriction: List[str] = None,
                 fetch_full_page: bool = False):
        super().__init__()
        task_id = str(int(time.time()))
        config: RunnableConfig = RunnableConfig(

            configurable={
                "thread_id": task_id,

                "number_of_queries": number_of_queries,
                "max_results_per_query": max_results_per_query,
                "max_search_depth": max_search_depth,

                "search_api": search_api,
                "sites_search_restriction": domains_search_restriction,
                "fetch_full_page": fetch_full_page,

                # uso modello proprietario
                # "planner_provider": "my_provider",
                # "planner_model": "gpt-4o-mini",
                # "writer_provider": "my_provider",
                # "writer_model": "gpt-4o-mini",

                # uso di openrouter
                "planner_provider": "openrouter",
                "planner_model": "mistralai/mistral-small-24b-instruct-2501:free",
                "writer_provider": "openrouter",
                "writer_model": "mistralai/mistral-small-24b-instruct-2501:free",
            }
        )
        self._config = config

        self._runner = LangGraphRunner()

        # Configura i callback per il runner
        self._runner.register_event_callback(self._on_graph_event)
        self._runner.register_state_change_callback(self._on_state_change)
        self._runner.register_completion_callback(self._on_completion)
        self._runner.register_abort_callback(self._on_abort)
        self._runner.register_error_callback(self._on_error)
        self._runner.register_timeout_callback(self._on_timeout)

    @staticmethod
    def _initiate_final_section_writing(state: DeepReportState):
        return [
            Send(WriteFinalSectionsAgent.Name,
                 SectionState(topic=state.topic, section=s,
                              report_sections_from_research=state.report_sections_from_research)
                 )
            for s in state.sections if not s.ricerca
        ]

    def _init_research_team(self) -> StateGraph:
        workflow = StateGraph(DeepReportState,
                              input=DeepReportStateInput,
                              # output=DeepReportStateOutput,   #todo: metteree in output solo valori che servono
                              config_schema=Configuration)

        # workflow nodes
        workflow.add_node(*ReportPlannerAgent.node())
        workflow.add_node(*HumanFeedbackAgent.node())
        workflow.add_node(*BuildSectionWithWebResearch.node())
        workflow.add_node(*GatherCompletedSections.node())
        workflow.add_node(*WriteFinalSectionsAgent.node())
        workflow.add_node(*CompileFinalReport.node())

        # workflow edges
        workflow.set_entry_point(ReportPlannerAgent.Name)
        workflow.add_edge(ReportPlannerAgent.Name, HumanFeedbackAgent.Name)
        workflow.add_edge(BuildSectionWithWebResearch.Name, GatherCompletedSections.Name)
        workflow.add_conditional_edges(GatherCompletedSections.Name,
                                       self._initiate_final_section_writing, [WriteFinalSectionsAgent.Name])
        workflow.add_edge(WriteFinalSectionsAgent.Name, CompileFinalReport.Name)
        workflow.add_edge(CompileFinalReport.Name, END)

        return workflow

    def _on_graph_event(self, event):
        """Callback per gli eventi del grafo"""
        print(f"EVENT: {event}")  # Per debug

        if '__interrupt__' in event:
            interrupt_value = event['__interrupt__'][0].value
            self.event_notify(event_data=EventData(event_type="INFO",
                                                   state=ProcessState.WaitingForApproval,
                                                   message=interrupt_value['question'],
                                                   data=interrupt_value['sections']))
            # per solo debug: input su console
            # human_response = input(interrupt_value['question'])
            # self._runner.provide_user_response(Command(resume=human_response))

    def plan_feedback(self, feedback):
        self._runner.provide_user_response(Command(resume=feedback))

    def approve(self):
        self._runner.provide_user_response(Command(resume="si"))

    def _on_state_change(self, new_state, current_state):
        """Callback per i cambiamenti di stato"""
        # per ora non usato
        pass

    def _on_completion(self, result):
        """Callback per il completamento dell'esecuzione"""
        self.event_notify(event_data=EventData(
            event_type="INFO",
            state=ProcessState.Completed,
            message="Esecuzione completata con successo",
            data={'final_report': result['final_report']}
        ))

        # salvataggio report finale
        if 'final_report' in result and result['final_report']:
            timestamp = time.strftime("%Y_%H%M")
            filename = f"final_report_{timestamp}.md"
            with open(filename, "w", encoding="utf-8") as md_file:
                md_file.write(result['final_report'])

    def _on_abort(self):
        """Callback per l'abort dell'esecuzione"""
        self.event_notify(event_data=EventData(
            event_type="INFO",
            message="Esecuzione interrotta dall'utente",
            state=ProcessState.Aborted,
            data={}
        ))

    def _on_timeout(self):
        """Callback per il timeout dell'esecuzione"""
        self.event_notify(event_data=EventData(
            event_type="INFO",
            message="Esecuzione interrotta per tmeout",
            state=ProcessState.Aborted,
            data={}
        ))
        pass

    def _on_error(self, error):
        """Callback per gli errori durante l'esecuzione"""
        self.event_notify(event_data=EventData(
            event_type="ERROR",
            state=ProcessState.Error,
            message=f"Errore durante l'esecuzione: {str(error)}",
            data={"error": str(error)}
        ))

    def invoke(self, topic: str):
        memory = MemorySaver()
        research_team = self._init_research_team()
        chain = research_team.compile(checkpointer=memory)
        initial_state = DeepReportState(topic=topic, sections=[], completed_sections=[])

        chain.get_graph().draw_mermaid_png(output_file_path="chief_deep_report_agent.png")

        self.event_notify(event_data=EventData(event_type="INFO", state=ProcessState.Started,
                                               message="start DeepReport Team agents", data={}))

        # uso con  LangGraphRunner() -----------------------------
        return self._runner.run(chain, initial_state, self._config, timeout=60 * 30, blocking=False)
        # --------------------------------------------------------

        # uso senza LangGraphRunner ----------------------------------------------
        # while True:
        #     for event in chain.stream(current_input, self._config, stream_mode="updates"):
        #         print(f"EVENT: {event}")
        #         if '__interrupt__' in event:
        #             interrupt_value = event['__interrupt__'][0].value
        #             if '__interrupt__' in event:
        #                 human_response = input(interrupt_value['question'])
        #                 current_input = Command(resume=human_response)
        #     if chain.get_state(self._config).next == ():
        #         break
        #
        # state = chain.get_state(self._config).values
        # return state

    def abort(self) -> bool:
        """Forza l'interruzione dell'esecuzione del grafo"""
        if self._runner.abort():
            self.event_notify(event_data=EventData(
                event_type="INFO",
                state=ProcessState.Aborted,
                message="Richiesta di interruzione inviata",
                data={}
            ))
            return True
        return False

    def is_running(self):
        """Controlla se il grafo è in esecuzione"""
        return self._runner.is_running()

    def get_result(self, timeout=None):
        """Ottiene il risultato dell'esecuzione, aspettando se necessario"""
        return self._runner.get_result(timeout=timeout)

    def get_current_state(self):
        """Ottiene lo stato corrente dell'esecuzione"""
        return self._runner.get_current_state()
