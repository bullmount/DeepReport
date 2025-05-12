from typing import Dict, Literal
from langchain_core.runnables import RunnableConfig

from agents.agent_base import DeepReportAgentBase
from agents.build_section_with_web_research import BuildSectionWithWebResearch
from agents.gather_completed_sections_agent import GatherCompletedSections
from deep_report_state import DeepReportState, Queries, Sections, SectionState
from langgraph.types import interrupt, Command
from langgraph.constants import Send

from event_notifier import ProcessState, EventData


class HumanFeedbackAgent(DeepReportAgentBase):
    Name = "human_feedback"

    def __init__(self):
        super().__init__()

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
        interrupt_message = f"""Per favore, fornisci un feedback sul seguente piano del report. 
                               
{sections_str}

Il piano del report soddisfa le tue esigenze?
Inserisci 'si' per approvare il piano del report.
Oppure, fornisci un feedback per rigenerare il piano del report:"""

        data = {
            "sezioni":
                [{
                    "posizione": s.posizione,
                    "titolo": s.nome,
                    "descrizione": s.descrizione,
                    "contenuto": s.contenuto,
                    "iteration_count": 0,
                    "richiede_ricerca": s.ricerca
                } for s in sections]
        }

        feedback = interrupt({"question": interrupt_message, "sections": data})

        if isinstance(feedback, str):
            if feedback.lower() == "si" or feedback.lower() == "ok":
                feedback = True

        if isinstance(feedback, bool) and feedback is True:
            self.event_notify(event_data=EventData(event_type="INFO",
                                                   state=ProcessState.Approved,
                                                   message="Piano approvato, redazione delle singole sezioni",
                                                   data=data))
            if len([s for s in sections if s.ricerca]) == 0:
                return Command(goto=GatherCompletedSections.Name,
                               update={})
            else:
                return Command(goto=[
                    Send(BuildSectionWithWebResearch.Name,
                         SectionState(topic=topic, section=s, all_sections=state.sections,
                                      search_iterations=0, web_research_results=[],
                                      bad_search_results=state.bad_search_results)
                         )
                    for s in sections if s.ricerca])
        elif isinstance(feedback, str):
            return Command(goto="generate_report_plan",
                           update={"feedback_on_report_plan": feedback})
        else:
            raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")
