from langchain_core.runnables import RunnableConfig

from deep_report_state import DeepReportState


class CompileFinalReport:
    Name: str = "compile_final_report"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke


    def invoke(self, state: DeepReportState, config: RunnableConfig):
        sections = state.sections
        completed_sections = {s.nome: s.contenuto for s in state.completed_sections}

        for section in sections:
            section.contenuto = completed_sections[section.nome]

        all_sections = "\n\n".join([s.contenuto for s in sections])

        return {"final_report": all_sections}
