from typing import Dict

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agents.agent_base import DeepReportAgentBase
from agents.generate_queries_agent import GenerateQueriesAgent
from agents.search_web_agent import SearchWebAgent
from agents.write_section_agent import WriteSectionAgent
from configuration import Configuration
from deep_report_state import SectionState, SectionOutputState
from langchain_core.runnables import RunnableConfig


class BuildSectionWithWebResearch(DeepReportAgentBase):
    Name = "build_section_with_web_research"

    def __init__(self):
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
        # res = self._graph.invoke(state, config)
        # return res

        current_state = None
        configurable = Configuration.from_runnable_config(config)
        for _ in self._graph.stream(state, config, stream_mode="updates"):
            if configurable.abort_signal.is_set():
                raise KeyboardInterrupt("Operation aborted by user")
            graph_state = self._graph.get_state(config)
            current_state = graph_state.values

        return {"completed_sections": current_state["completed_sections"]}
