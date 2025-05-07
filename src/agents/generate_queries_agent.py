from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agents.agent_base import DeepReportAgentBase, EventData
from configuration import Configuration
from deep_report_state import SectionState, Queries
from event_notifier import ProcessState, LoadSectionData, FaseSezione
from prompts import query_writer_instructions
from utils.json_extractor import parse_model
from utils.llm_provider import llm_provide
from utils.utils import get_config_value, get_current_date, estrai_sezioni_markdown_e_indice_assegnata


class GenerateQueriesAgent(DeepReportAgentBase):
    Name: str = "generate_queries"

    def __init__(self):
        super().__init__()

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        self.event_notify(event_data=EventData(event_type="INFO",
                                               state=ProcessState.WritingSection,
                                               message="Preparazione query di ricerca",
                                               data=dict(LoadSectionData(state, FaseSezione.QUERY))))
        topic = state.topic
        section = state.section
        section_number, other_sections = estrai_sezioni_markdown_e_indice_assegnata(state.all_sections, state.section)

        configurable = Configuration.from_runnable_config(config)
        number_of_queries = configurable.number_of_queries

        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)

        structured_llm = llm_provide(writer_model_name, writer_provider)

        system_instructions = query_writer_instructions.format(topic=topic,
                                                               current_date=get_current_date(),
                                                               section_number=section_number,
                                                               section_title=section.nome,
                                                               section_description=section.descrizione,
                                                               other_sections=other_sections,
                                                               number_of_queries=number_of_queries,
                                                               json_format=Queries.model_json_schema())
        results = structured_llm.invoke([SystemMessage(content=system_instructions),
                                         HumanMessage(
                                             content=f"Genera query di ricerca per l'argomento della sezione numero {section_number}.")],
                                             response_format=Queries.model_json_schema())
        queries: Queries = parse_model(Queries, results.content)

        return {"search_queries": queries.queries}
