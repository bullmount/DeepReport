import time
from langgraph.graph import END, StateGraph, START
from langchain_core.runnables import RunnableConfig
from agents import ReportPlannerAgent
from agents.build_section_with_web_research import BuildSectionWithWebResearch
from agents.gather_completed_sections_agent import GatherCompletedSections
from agents.generate_queries_agent import GenerateQueriesAgent
from agents.human_feedback_agent import HumanFeedbackAgent
from agents.search_web_agent import SearchWebAgent
from agents.write_section_agent import WriteSectionAgent
from configuration import Configuration
from deep_report_state import DeepReportState, DeepReportStateInput, DeepReportStateOutput, SectionState, \
    SectionOutputState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import  Command


class ChiefDeepReportAgent:
    def __init__(self):
        task_id = str(int(time.time()))
        config: RunnableConfig = RunnableConfig(

            configurable={
                "thread_id": task_id,
                #         "search_api": "google",
                #         # "site_search_restriction": "dominio",
                #         "fetch_full_page": True,
                #
                #         "llm_provider": "openrouter",
                #         # # "model_name": "google/gemma-3-27b-it:free",
                #         "model_name": "mistralai/mistral-small-24b-instruct-2501:free",
                #
                #         # sistema interno privato ----------
                #         # "llm_provider": "my_provider",
                #         # "model_name": "gpt-4o",
                #         # "model_name": "gpt-4o-mini",
                #
            }
        )
        self._config = config

    def _init_research_team(self) -> StateGraph:
        workflow = StateGraph(DeepReportState,
                              input=DeepReportStateInput, output=DeepReportStateOutput,
                              config_schema=Configuration)

        # section writer sub-workflow
        section_workflow = StateGraph(SectionState, output=SectionOutputState)
        section_workflow.add_node(*GenerateQueriesAgent.node())
        section_workflow.add_node(*SearchWebAgent.node())
        section_workflow.add_node(*WriteSectionAgent.node())

        # Add edges
        section_workflow.add_edge(START, GenerateQueriesAgent.Name)
        section_workflow.add_edge(GenerateQueriesAgent.Name, SearchWebAgent.Name)
        section_workflow.add_edge(SearchWebAgent.Name, WriteSectionAgent.Name)

        # workflow nodes
        workflow.add_node(*ReportPlannerAgent.node())
        workflow.add_node(*HumanFeedbackAgent.node())
        workflow.add_node(BuildSectionWithWebResearch.Name,section_workflow.compile())
        # workflow.add_node(*BuildSectionWithWebResearch.node())
        workflow.add_node(*GatherCompletedSections.node())

        # workflow edges
        workflow.set_entry_point(ReportPlannerAgent.Name)
        workflow.add_edge(ReportPlannerAgent.Name, HumanFeedbackAgent.Name)
        workflow.add_edge(BuildSectionWithWebResearch.Name, GatherCompletedSections.Name)
        # todo:  altra parte di grafo
        workflow.add_edge(GatherCompletedSections.Name, END)

        return workflow

    async def run_research_task(self, task_id=None):
        pass

    def invoke(self, topic: str):
        memory = MemorySaver()
        research_team = self._init_research_team()
        chain = research_team.compile(checkpointer=memory)
        initial_state = DeepReportState(topic=topic, sections=[],
                                        completed_sections=[])

        chain.get_graph().draw_mermaid_png(output_file_path="chief_deep_report_agent.png")

        # todo: remove
        # res = chain.invoke(initial_state, config=self._config)

        current_input = initial_state

        while True:
            for event in chain.stream(current_input, self._config, stream_mode="updates"):
                if '__interrupt__' in event:
                    interrupt_value = event['__interrupt__'][0].value
                    if '__interrupt__' in event:
                        interrupt_value = event['__interrupt__'][0].value
                        human_response = "si" # input(interrupt_value['question'])
                        current_input = Command(resume=human_response)
            if chain.get_state(self._config).next == ():
                break

        state = chain.get_state(self._config).values
        return state