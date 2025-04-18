from typing import Dict

from langchain_core.runnables import RunnableConfig

from deep_report_state import DeepReportState


class GatherCompletedSections():
    def __init__(self):
        pass

    def invoke(self, state: DeepReportState, config: RunnableConfig) -> Dict[str, any]:
        return {}
