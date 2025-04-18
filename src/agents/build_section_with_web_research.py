import os
from typing import Dict, Literal
from deep_report_state import DeepReportState, SectionState
from langchain_core.runnables import RunnableConfig

# todo: rimuovere e mettere al suo interino il sotto grafo
class BuildSectionWithWebResearch:
    Name = "build_section_with_web_research"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        print(f"\nBuildSectionWithWebResearch: {state.section.nome}")
        return {"completed_sections": [f"contenuto di {state.section.nome} generato con successo"]}
