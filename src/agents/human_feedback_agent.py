import os
from typing import Dict, Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from configuration import Configuration
from deep_report_state import DeepReportState, Queries, Sections, SectionState
from prompts import report_planner_query_writer_instructions, report_planner_instructions
from search_system import SearchSystem
from utils.json_extractor import parse_model
from utils.llm_provider import llm_provide
from utils.sources_formatter import SourcesFormatter
from utils.utils import get_config_value
from langchain.chat_models import init_chat_model
from langgraph.types import interrupt, Command
from langgraph.constants import Send



class HumanFeedbackAgent():
    Name = "human_feedback"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: DeepReportState,
               config: RunnableConfig) -> Command[Literal["generate_report_plan", "build_section_with_web_research"]]:

        topic = state.topic
        sections = state.sections

        sections_str = "\n\n".join(
            f"Sezione: {section.nome}\n"
            f"Descrizione: {section.descrizione}\n"
            f"Ricerca web necessaria: {'SI' if section.ricerca else 'NO'}\n"
            for section in sections
        )

        # Get feedback on the report plan from interrupt
        interrupt_message = f"""Please provide feedback on the following report plan. 
                               \n\n{sections_str}\n
                               \nDoes the report plan meet your needs?\nPass 'true' to approve the report plan.\nOr, provide feedback to regenerate the report plan:"""

        feedback = interrupt({"question":interrupt_message})

        if isinstance(feedback, str):
            if feedback.lower() == "si" or feedback.lower() == "ok":
                feedback = True

        # If the user approves the report plan, kick off section writing
        if isinstance(feedback, bool) and feedback is True:
            # Treat this as approve and kick off section writing
            return Command(goto=[
                Send("build_section_with_web_research",
                     SectionState(topic=topic,section=s,search_iterations=0)
                     # {"topic": topic, "section": s, "search_iterations": 0}
                    )
                for s in sections if s.ricerca])
        elif isinstance(feedback, str):
            return Command(goto="generate_report_plan",
                           update={"feedback_on_report_plan": feedback})
        else:
            raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")
