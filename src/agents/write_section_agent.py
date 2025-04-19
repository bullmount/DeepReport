from typing import Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from agents.search_web_agent import SearchWebAgent
from configuration import Configuration
from deep_report_state import SectionState, Feedback
from langgraph.graph import  END
from langgraph.types import Command

from prompts import section_writer_inputs, section_writer_instructions, section_grader_instructions
from utils.json_extractor import parse_model
from utils.llm_provider import llm_provide
from utils.utils import get_config_value


class WriteSectionAgent:
    Name = "write_section"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig):
        topic = state.topic
        section = state.section
        source_str = state.source_str

        configurable = Configuration.from_runnable_config(config)
        section_writer_inputs_formatted = section_writer_inputs.format(topic=topic,
                                                                       section_name=section.nome,
                                                                       section_topic=section.descrizione,
                                                                       context=source_str,
                                                                       section_content=section.contenuto)

        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)
        writer_model = llm_provide(writer_model_name, writer_provider)
        section_content = writer_model.invoke([SystemMessage(content=section_writer_instructions),
                                               HumanMessage(content=section_writer_inputs_formatted)])

        section.contenuto = section_content.content

        # Grade prompt
        section_grader_message = (
            "Valuta il rapporto e considera domande di approfondimento per eventuali informazioni mancanti. "
            "Se la valutazione è 'pass', restituisci stringhe vuote per tutte le domande di approfondimento. "
            "Se la valutazione è 'fail', fornisci query di ricerca specifiche per raccogliere le informazioni mancanti.")

        section_grader_instructions_formatted = section_grader_instructions.format(topic=topic,
                                                                                   section_topic=section.descrizione,
                                                                                   section=section.contenuto,
                                                                                   json_format=Feedback.model_json_schema(),
                                                                                   number_of_follow_up_queries=configurable.number_of_queries)

        planner_provider = get_config_value(configurable.planner_provider)
        planner_model = get_config_value(configurable.planner_model)
        reflection_model = llm_provide(planner_model, planner_provider)

        results = reflection_model.invoke([SystemMessage(content=section_grader_instructions_formatted),
                                           HumanMessage(content=section_grader_message)])

        feedback: Feedback = parse_model(Feedback, results.content)

        if feedback.grade == "pass" or state.search_iterations >= configurable.max_search_depth:
            return Command(
                update={"completed_sections": [section]}, goto=END)
        else:
            return Command(
                update={"search_queries": feedback.follow_up_queries, "section": section},
                goto=SearchWebAgent.Name
            )

        return {"completed_sections": [section]}
