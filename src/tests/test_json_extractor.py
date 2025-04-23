from deep_report_state import Sections
from utils.json_extractor import parse_model


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