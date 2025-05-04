from pathlib import Path
from typing import Dict
from langchain_core.runnables import RunnableConfig
from deep_report_state import DeepReportState, Sections
from utils.traccia_tempo import time_tracker
from utils.utils import format_sections


class GatherCompletedSections():
    Name: str = "gather_completed_sections"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    @time_tracker
    def invoke(self, state: DeepReportState, config: RunnableConfig) -> Dict[str, any]:
        completed_sections = state.completed_sections

        completed_sections_per_nome = {s.nome: s for s in completed_sections}
        completed_sections = []
        for section in state.sections:
            if not section.ricerca:
                section.contenuto = "[sezione ancora non scritta]"
            else:
                section.contenuto = completed_sections_per_nome[section.nome].contenuto
                section.sources = completed_sections_per_nome[section.nome].sources
            completed_sections.append(section)

        # todo: remove -------------------
        sections = Sections(sezioni=completed_sections)
        output_path = Path("completed_sections.json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sections.model_dump_json(indent=4))
        # --------------------------------

        completed_report_sections = format_sections(completed_sections)
        return {"report_sections_from_research": completed_report_sections}
