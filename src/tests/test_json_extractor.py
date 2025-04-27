from deep_report_state import Sections, SectionReview
from utils.json_extractor import parse_model
import json
from typing import Type, Optional, List, Any
import tolerantjson
from jsonfinder import jsonfinder
import re
from pydantic import BaseModel, ValidationError

def escape_newlines_in_quotes(s: str) -> str:
    """
    Per ogni porzione di testo tra doppi apici non preceduti da backslash,
    sostituisce i caratteri di newline con la sequenza '\\n'.
    """

    # Pattern: "(…)" ma solo se il " iniziale non è preceduto da backslash
    pattern = re.compile(r'(?<!\\)"(.*?)"', flags=re.DOTALL)

    def _repl(match: re.Match) -> str:
        # match.group(1) è il contenuto interno a "…"
        inner = match.group(1)
        # eseguo la sostituzione
        inner_escaped = inner.replace('\n', '\\n')
        # ricostruisco il blocco con le virgolette
        return f'"{inner_escaped}"'

    # Applico la sostituzione a tutta la stringa
    return pattern.sub(_repl, s)


def find_and_validate_jsons_flexible(llm_output: str, pydantic_model: Type[BaseModel]) -> Optional[List[BaseModel]]:

    potential_jsons = []

    def find_matching(text: str, start_index: int, open_char: str, close_char: str) -> Optional[str]:
        count = 1
        for i in range(start_index + 1, len(text)):
            if text[i] == open_char:
                count += 1
            elif text[i] == close_char:
                count -= 1
                if count == 0:
                    return text[start_index : i + 1]
        return None

    # Trova tutte le coppie di graffe
    start = 0
    while True:
        start_brace = llm_output.find('{', start)
        if start_brace == -1:
            break
        json_str = find_matching(llm_output, start_brace, '{', '}')
        if json_str:
            potential_jsons.append(json_str)
            start = start_brace + 1
        else:
            start += 1

    # Trova tutte le coppie di parentesi quadre
    start = 0
    while True:
        start_bracket = llm_output.find('[', start)
        if start_bracket == -1:
            break
        json_str = find_matching(llm_output, start_bracket, '[', ']')
        if json_str:
            potential_jsons.append(json_str)
            start = start_bracket + 1
        else:
            start += 1

    if not potential_jsons:
        print("Nessun potenziale blocco JSON trovato nella stringa.")
        return None

    # Ordina i potenziali JSON per dimensione decrescente
    potential_jsons.sort(key=len, reverse=True)

    for json_str in potential_jsons:
        try:
            json_str = escape_newlines_in_quotes(json_str)
            data = json.loads(json_str)
            validated_result = _validate_data(data, pydantic_model)
            if validated_result:
                return validated_result
        except json.JSONDecodeError:
            pass  # Tenta il prossimo blocco JSON

    print("Nessun blocco JSON valido trovato che corrisponda al modello Pydantic.")
    return None


def _validate_data(data: Any, pydantic_model: Type[BaseModel]) -> Optional[List[BaseModel]]:
    validated_items = []
    if isinstance(data, list):
        for item in data:
            try:
                validated_items.append(pydantic_model(**item))
            except ValidationError as e:
                print(f"Errore di validazione Pydantic per un elemento dell'array: {e}")
                return None
        return validated_items
    elif isinstance(data, dict):
        try:
            validated_items.append(pydantic_model(**data))
            return validated_items
        except ValidationError as e:
            print(f"Errore di validazione Pydantic per l'oggetto: {e}")
            return None
    else:
        print("Il JSON estratto non è né un oggetto né un array valido per la validazione.")
        return None

def test_parse_model():
    json_str = """
'{\n  "new_section_content": "## Metodologia di Valutazione del Rischio\\n\\nIl modello MoVaRisCh 2025 adotta un approccio innovativo per la valutazione del rischio chimico, permettendo di calcolare il rischio senza la necessità di misurazioni dirette. Questo è particolarmente vantaggioso per le piccole e medie imprese (PMI) che potrebbero non avere accesso a strumenti di misurazione avanzati. La metodologia si basa su un algoritmo matematico che combina due elementi fondamentali: la pericolosità intrinseca di una sostanza (P) e il livello di esposizione (E) a cui i lavoratori sono sottoposti. Il risultato di questa combinazione è un indice numerico del rischio (R), calcolato attraverso la formula:\\n\\n**R = P x E**.\\n\\n### Componenti del Calcolo del Rischio\\n\\n1. **Pericolo (P)**:\\n   - Rappresenta la pericolosità intrinseca di una sostanza o miscela, definita in base alle frasi di rischio (H) del Regolamento CLP (CE n. 1272/2008).\\n   - Ogni indicazione di pericolo H è associata a un punteggio che riflette la gravità del rischio, con particolare attenzione agli effetti a lungo termine come cancerogenicità, mutagenicità e tossicità per la riproduzione.\\n\\n2. **Esposizione (E)**:\\n   - L\'esposizione è suddivisa in due categorie: inalatoria (Einal) e cutanea (Ecute).\\n   - I fattori considerati per calcolare l\'esposizione includono:\\n     - Quantità di sostanza utilizzata.\\n     - Tipo di utilizzo.\\n     - Misure di controllo adottate.\\n     - Tempo di esposizione.\\n\\n### Algoritmo di Calcolo\\n\\nIl modello utilizza un algoritmo che assegna un valore numerico a una serie di fattori, pesando l\'importanza di ciascuno di essi. Questo processo include:\\n\\n- Identificazione dei parametri che determinano il rischio.\\n- Assegnazione di un \\"peso\\" ai fattori di compensazione.\\n- Definizione della relazione numerica tra i parametri (additivi, moltiplicativi, esponenziali, ecc.).\\n- Creazione di una scala di valori per l\'indice di rischio, che consente di classificare il rischio in diverse fasce.\\n\\n### Classificazione del Rischio\\n\\nIl rischio calcolato viene poi classificato in fasce che vanno da \\"irrilevante\\" a \\"grave\\", con soglie di intervento specifiche. Questa classificazione aiuta le PMI a comprendere meglio il livello di rischio e a prendere decisioni informate riguardo alle misure di prevenzione e protezione da adottare. Le fasce di rischio definite dal modello sono:\\n- R < 15: rischio irrilevante per la salute (zona verde).\\n- R tra 15 e 20: intervallo di incertezza (zona arancione), con revisione delle misure preventive e protettive e consultazione obbligatoria del medico competente.\\n- R tra 21 e 40: rischio superiore all’irrilevante, con applicazione di misure specifiche previste dagli articoli 225, 226, 229 e 230 del D.Lgs.81/08.\\n- R tra 41 e 80: rischio elevato.\\n- R > 80: rischio grave, che impone una completa revisione delle misure di prevenzione e protezione, intensificazione delle attività di sorveglianza sanitaria e misurazioni ambientali [3].\\n\\nIn sintesi, la metodologia di valutazione del rischio del MoVaRisCh 2025 offre un approccio semplice e scientifico, consentendo alle PMI di gestire il rischio chimico in modo efficace e conforme alle normative vigenti, senza la necessità di misurazioni dirette.",\n  "grade": "RESEARCH",\n  "follow_up_queries": [\n    {\n      "search_query": "approfondimenti sulla metodologia di valutazione del rischio chimico MoVaRisCh 2025"\n    },\n    {\n      "search_query": "novità nella classificazione del rischio chimico secondo MoVaRisCh 2025"\n    }\n  ]\n}'

    """
    section_review: SectionReview = parse_model(SectionReview, json_str)
    print(section_review.new_section_content)

def test_json_extractor():
    json = """```json
{
  "sezioni": [
    {
      "nome": "Introduzione",
      "descrizione": "Breve panoramica dell'area tematica relativa agli ultimi aggiornamenti sulla formazione in materia di sicurezza sul lavoro secondo l'Accordo Stato-Regioni.",
      "ricerca": false,
      "contenuto": ""
    },
    {
      "nome": "Contesto Normativo e Obiettivi dell'Accordo",
      "descrizione": "Descrizione del contesto normativo che ha portato alla necessità di un nuovo accordo e gli obiettivi principali che si intendono raggiungere con l'Accordo Stato-Regioni del 2025.",
      "ricerca": true,
      "contenuto": ""
    },
    {
      "nome": "Principali Novità dell'Accordo 2025",
      "descrizione": "Analisi delle principali novità introdotte dall'Accordo del 2025, inclusi i cambiamenti nella durata e nei contenuti minimi dei percorsi formativi.",
      "ricerca": true,
      "contenuto": ""
    },
    {
      "nome": "Implicazioni per le Aziende",
      "descrizione": "Esame delle implicazioni pratiche per le aziende, inclusi gli aggiornamenti necessari ai piani formativi e le nuove modalità di erogazione della formazione.",
      "ricerca": true,
      "contenuto": ""
    },
    {
      "nome": "Conclusione",
      "descrizione": "Sintesi delle sezioni principali e riassunto conciso del report, con un elemento strutturale che sintetizza le informazioni chiave.",
      "ricerca": false,
      "contenuto": ""
    }
  ]
}
```"""
    sections: Sections = parse_model(Sections, json)
    assert True, "lettura json non effettuata con successo"