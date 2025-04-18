import os
from typing import Dict, Literal

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agents.generate_queries_agent import GenerateQueriesAgent
from agents.search_web_agent import SearchWebAgent
from agents.write_section_agent import WriteSectionAgent
from deep_report_state import DeepReportState, SectionState, SectionOutputState
from langchain_core.runnables import RunnableConfig


# todo: rimuovere e mettere al suo interino il sotto grafo
class BuildSectionWithWebResearch:
    Name = "build_section_with_web_research"

    def __init__(self):
        # section writer sub-workflow
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
        print(f"\nBuildSectionWithWebResearch: {state.section.nome}")
        return res
