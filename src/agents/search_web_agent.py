from typing import Dict
from langchain_core.runnables import RunnableConfig
from deep_report_state import SectionState


class SearchWebAgent():
    Name: str = "search_web"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        return {"source_str": "source str from web", "search_iterations": state.search_iterations + 1}

