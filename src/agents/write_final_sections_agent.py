from typing import Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from deep_report_state import SectionState
from prompts import final_section_writer_instructions
from utils.llm_provider import llm_provide
from utils.traccia_tempo import time_tracker
from utils.utils import get_config_value


class WriteFinalSectionsAgent:
    Name: str = "write_final_sections"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    @time_tracker
    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        configurable = Configuration.from_runnable_config(config)

        #TODO: DISTINGUERE PER TIPO SEZIONE

        topic = state.topic
        section = state.section
        completed_report_sections = state.report_sections_from_research

        system_instructions = final_section_writer_instructions.format(topic=topic,
                                                                       section_name=section.nome,
                                                                       section_topic=section.descrizione,
                                                                       context=completed_report_sections)

        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)
        writer_model = llm_provide(writer_model_name, writer_provider)

        section_content = writer_model.invoke([SystemMessage(content=system_instructions),
                                               HumanMessage(
                                                   content="Genera una sezione del report basata sulle fonti fornite.")])
        section.contenuto = section_content.content
        return {"completed_sections": [section]}
