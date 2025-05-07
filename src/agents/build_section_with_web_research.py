from typing import Dict

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agents.agent_base import DeepReportAgentBase, EventData
from agents.generate_queries_agent import GenerateQueriesAgent
from agents.search_web_agent import SearchWebAgent
from agents.write_section_agent import WriteSectionAgent
from deep_report_state import  SectionState, SectionOutputState
from langchain_core.runnables import RunnableConfig


class BuildSectionWithWebResearch(DeepReportAgentBase):
    Name = "build_section_with_web_research"

    def __init__(self):
        # section writer sub-workflow
        super().__init__()
        workflow = StateGraph(SectionState, output=SectionOutputState)
        workflow.add_node(*GenerateQueriesAgent.node())
        workflow.add_node(*SearchWebAgent.node())
        workflow.add_node(*WriteSectionAgent.node())

        # Add edges
        workflow.add_edge(START, GenerateQueriesAgent.Name)
        workflow.add_edge(GenerateQueriesAgent.Name, SearchWebAgent.Name)
        workflow.add_edge(SearchWebAgent.Name, WriteSectionAgent.Name)
        workflow.add_edge(WriteSectionAgent.Name, END)

        self._graph = workflow.compile()

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        res = self._graph.invoke(state, config)
        return res
