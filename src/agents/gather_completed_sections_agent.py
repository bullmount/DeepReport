from typing import Dict

from langchain_core.runnables import RunnableConfig

from deep_report_state import DeepReportState


class GatherCompletedSections():
    Name: str = "gather_completed_sections"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: DeepReportState, config: RunnableConfig) -> Dict[str, any]:
        return {}
