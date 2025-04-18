from typing import Dict
from langchain_core.runnables import RunnableConfig
from deep_report_state import SectionState
from tests.test_json_schema import SearchQuery


class GenerateQueriesAgent:
    Name: str = "generate_queries"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        topic = state.topic
        section = state.section

        dummy = [
            SearchQuery(search_query="dummy query 1"),
            SearchQuery(search_query="dummy query 2")
        ]
        return {"search_queries": dummy}
