from typing import Dict
from langchain_core.runnables import RunnableConfig
from deep_report_state import SectionState
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from typing import Literal

class WriteSectionAgent:
    Name = "write_section"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState,
               config: RunnableConfig) -> Command[Literal[END, "search_web"]]:
        topic = state.topic
        section = state.section
        source_str = state.source_str
        section.contenuto = "contenuto della sezione"

        return Command(update={"completed_sections": [section]}, goto=END)
