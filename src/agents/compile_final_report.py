from typing import Tuple, List, Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from deep_report_state import DeepReportState, Section
from prompts import final_report_writer_instructions
from search_engines.search_engine_base import SearchEngResult
from utils.llm_provider import llm_provide
from utils.sources_formatter import SourcesFormatter
from utils.utils import get_config_value
import re


def remap_sources(sezioni: List[Section]) -> Tuple[List[Section], List[SearchEngResult]]:
    url_to_new_number: Dict[str, int] = {}
    nuova_lista_fonti: List[str] = []
    prossimo_numero = 1

    elenco_unico_fonti: List[SearchEngResult] = []
    sezioni_aggiornate: List[Section] = []
    for sezione in sezioni:
        mappa_vecchio_nuovo: Dict[int, int] = {}
        for fonte in sezione.sources:
            if fonte['url'] not in url_to_new_number:
                url_to_new_number[fonte['url']] = prossimo_numero
                nuova_lista_fonti.append(fonte['url'])
                x = fonte.copy()
                x['num_source'] = prossimo_numero
                elenco_unico_fonti.append(x)
                prossimo_numero += 1
            mappa_vecchio_nuovo[fonte["num_source"]] = url_to_new_number[fonte["url"]]

        def sostituisci(match):
            vecchio_numero = int(match.group(1))
            nuovo_numero = mappa_vecchio_nuovo.get(vecchio_numero, vecchio_numero)
            return f"[{nuovo_numero}]"

        sezione_aggiornata = sezione.model_copy()

        if len(sezione.sources) > 0:
            sezione_aggiornata.contenuto = re.sub(r'\[(\d+)\]', sostituisci, sezione_aggiornata.contenuto)
        sezioni_aggiornate.append(sezione_aggiornata)

    return sezioni_aggiornate, elenco_unico_fonti


class CompileFinalReport:
    Name: str = "compile_final_report"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: DeepReportState, config: RunnableConfig):
        sections = state.sections

        completed_sections = {s.nome: s for s in state.completed_sections}
        for section in sections:
            section.contenuto = completed_sections[section.nome].contenuto
            section.sources = completed_sections[section.nome].sources

        # fusione delle fonti con rimappataura delle citazioni
        sezioni_rimappate, elenco_fonti_totale = remap_sources(sections)

        all_sections = "\n\n".join([s.contenuto for s in sezioni_rimappate])

        # review complessiva per rendere il testo più fluido
        configurable = Configuration.from_runnable_config(config)
        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)
        writer_model = llm_provide(writer_model_name, writer_provider)
        report_writer_inputs_formatted = final_report_writer_instructions.format(report_text=all_sections)

        section_content = writer_model.invoke([SystemMessage(content=report_writer_inputs_formatted),
                                               HumanMessage(
                                                   content="Riscrivi il report completo secondo le istruzioni date.")])

        # aggiunta in fondo delle fonti numerate
        final_report = section_content.content
        if len(elenco_fonti_totale) > 0:
            sources_formatter = SourcesFormatter()
            riepiloghi = sources_formatter.format_riepilogo(elenco_fonti_totale)
            final_report = final_report + "\n\n## FONTI:\n" + riepiloghi

        return {"final_report": final_report}
