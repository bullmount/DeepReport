from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from deep_report_state import SectionState, Queries
from prompts import query_writer_instructions
from utils.json_extractor import parse_model
from utils.llm_provider import llm_provide
from utils.utils import get_config_value, get_current_date


class GenerateQueriesAgent:
    Name: str = "generate_queries"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        topic = state.topic
        section = state.section

        configurable = Configuration.from_runnable_config(config)
        number_of_queries = configurable.number_of_queries

        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)

        structured_llm = llm_provide(writer_model_name, writer_provider)

        system_instructions = query_writer_instructions.format(topic=topic,
                                                               current_date = get_current_date(),
                                                               section_topic=section.descrizione,
                                                               number_of_queries=number_of_queries,
                                                               json_format=Queries.model_json_schema())
        results = structured_llm.invoke([SystemMessage(content=system_instructions),
                                         HumanMessage(content="Genera query di ricerca sull’argomento fornito.")])
        queries: Queries = parse_model(Queries, results.content)

        return {"search_queries": queries.queries}
