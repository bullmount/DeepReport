import os
from typing import Dict, Literal
from deep_report_state import DeepReportState,SectionState
from langchain_core.runnables import RunnableConfig

class BuildSectionWithWebResearch:
    def __init__(self):
        pass

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        print(f"\nBuildSectionWithWebResearch: {state.section.nome}")
        return {"completed_sections":[f"contenuto di {state.section.nome} generato con successo"]}