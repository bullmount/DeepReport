import os
from pathlib import Path
from typing import Dict, Literal
from langchain_core.runnables import RunnableConfig
from agents.gather_completed_sections_agent import GatherCompletedSections
from deep_report_state import DeepReportState, Queries, Sections, SectionState
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
        interrupt_message = f"""Per favore, fornisci un feedback sul seguente piano del rapporto. 
                               
{sections_str}

Il piano del rapporto soddisfa le tue esigenze?
Inserisci 'true' per approvare il piano del rapporto.
Oppure, fornisci un feedback per rigenerare il piano del rapporto:"""

        feedback = interrupt({"question": interrupt_message})

        # todo: remove -------------------------------
        file_path = Path("completed_sections.json")
        if file_path.exists():
            data = file_path.read_text(encoding="utf-8")
            sections_loaded = Sections.model_validate_json(data)
            return Command(update={"completed_sections": sections_loaded.sezioni},
                           goto=GatherCompletedSections.Name)
        # --------------------------------------

        if isinstance(feedback, str):
            if feedback.lower() == "si" or feedback.lower() == "ok":
                feedback = True

        if isinstance(feedback, bool) and feedback is True:
            if len([s for s in sections if s.ricerca]) == 0:
                return Command(goto=GatherCompletedSections.Name,
                               update={})
            else:
                return Command(goto=[
                    Send("build_section_with_web_research",
                         SectionState(topic=topic, section=s, search_iterations=0)
                         )
                    for s in sections if s.ricerca])
        elif isinstance(feedback, str):
            return Command(goto="generate_report_plan",
                           update={"feedback_on_report_plan": feedback})
        else:
            raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")
