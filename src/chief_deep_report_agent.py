import os
import time
from enum import Enum
from langgraph.graph import END, StateGraph, START
from langchain_core.runnables import RunnableConfig
from agents import ReportPlannerAgent
from agents.build_section_with_web_research import BuildSectionWithWebResearch
from agents.gather_completed_sections_agent import GatherCompletedSections
from agents.human_feedback_agent import HumanFeedbackAgent
from configuration import Configuration
from deep_report_state import DeepReportState, DeepReportStateInput, DeepReportStateOutput
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Markdown
from IPython.display import Image, display
from langgraph.types import interrupt, Command

class Agents(Enum):
    GENERATE_REPORT_PLAN = "generate_report_plan"
    HUMAN_FEEDBACK = "human_feedback"
    BUILD_SECTION_WITH_WEB_RESEARCH = "build_section_with_web_research"
    GATHER_COMPLETED_SECTIONS = "gather_completed_sections"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    LINKUP = "linkup"
    DUCKDUCKGO = "duckduckgo"
    GOOGLESEARCH = "googlesearch"


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

    def _init_research_team(self):
        agents = self._initialize_agents()
        return self._create_workflow(agents)

    # def _generate_task_id(self):
    #     return int(time.time())

    def _initialize_agents(self):
        return {
            Agents.GENERATE_REPORT_PLAN.value: ReportPlannerAgent(),
            Agents.HUMAN_FEEDBACK.value: HumanFeedbackAgent(),
            Agents.BUILD_SECTION_WITH_WEB_RESEARCH.value: BuildSectionWithWebResearch(),
            Agents.GATHER_COMPLETED_SECTIONS.value: GatherCompletedSections()
        }

    def _create_workflow(self, agents):
        workflow = StateGraph(DeepReportState,
                              input=DeepReportStateInput, output=DeepReportStateOutput,
                              config_schema=Configuration)

        workflow.add_node(Agents.GENERATE_REPORT_PLAN.value, agents[Agents.GENERATE_REPORT_PLAN.value].invoke)
        workflow.add_node(Agents.HUMAN_FEEDBACK.value, agents[Agents.HUMAN_FEEDBACK.value].invoke)
        workflow.add_node(Agents.BUILD_SECTION_WITH_WEB_RESEARCH.value,
                          agents[Agents.BUILD_SECTION_WITH_WEB_RESEARCH.value].invoke)
        workflow.add_node(Agents.GATHER_COMPLETED_SECTIONS.value,
                          agents[Agents.GATHER_COMPLETED_SECTIONS.value].invoke)

        # workflow edges
        workflow.set_entry_point(Agents.GENERATE_REPORT_PLAN.value)
        workflow.add_edge(Agents.GENERATE_REPORT_PLAN.value, Agents.HUMAN_FEEDBACK.value)
        workflow.add_edge(Agents.BUILD_SECTION_WITH_WEB_RESEARCH.value, Agents.GATHER_COMPLETED_SECTIONS.value)

        workflow.add_edge(Agents.GATHER_COMPLETED_SECTIONS.value, END)
        # workflow.add_edge(str(Agents.GENERATE_REPORT_PLAN), END)

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

        # res = chain.invoke(initial_state, config=self._config)
        # hres = input("ciao")
        # res = chain.invoke(Command(resume=hres), config=self._config)

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