from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from agents.search_web_agent import SearchWebAgent
from configuration import Configuration
from deep_report_state import SectionState, Feedback, Queries, SectionReview
from langgraph.graph import END
from langgraph.types import Command

from prompts import section_grader_instructions_initial, section_writer_instructions_initial, \
    section_writer_instructions_review
from utils.json_extractor import parse_model
from utils.llm_provider import llm_provide
from utils.sources_formatter import SourcesFormatter
from utils.utils import get_config_value, estrai_sezioni_markdown_e_indice_assegnata


class WriteSectionAgent:
    Name = "write_section"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig):
        configurable = Configuration.from_runnable_config(config)

        topic = state.topic
        section = state.section

        most_recent_web_research = state.web_research_results[-1]
        sources_formatter = SourcesFormatter()
        formatted_sources = sources_formatter.format_sources(most_recent_web_research,
                                                             include_raw_content=True,
                                                             max_tokens_per_source=3000,
                                                             numbering=True)

        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)
        writer_model = llm_provide(writer_model_name, writer_provider)
        section_number, report_structure = estrai_sezioni_markdown_e_indice_assegnata(state.all_sections,
                                                                                      state.section,
                                                                                      include_assegnata=True)
        previous_search_queries = "\n".join(
            [f"{i + 1}. {q.search_query}" for i, q in enumerate(state.previous_search_queries)])

        if state.search_iterations <= 1:  # caso di prima scrittura
            section_writer_inputs_formatted = section_writer_instructions_initial.format(topic=topic,
                                                                                         report_structure=report_structure,
                                                                                         section_number=section_number,
                                                                                         total_sections=len(
                                                                                             state.all_sections),
                                                                                         section_title=section.nome,
                                                                                         section_description=section.descrizione,
                                                                                         search_results=formatted_sources,
                                                                                         )

            section_content = writer_model.invoke([SystemMessage(content=section_writer_inputs_formatted),
                                                   HumanMessage(content="Genera la sezione del report.")])

            section.contenuto = section_content.content

            section_grader_instructions_formatted = section_grader_instructions_initial.format(topic=topic,
                                                                                               report_structure=report_structure,
                                                                                               section_number=section_number,
                                                                                               total_sections=len(
                                                                                                   state.all_sections),
                                                                                               section_title=section.nome,
                                                                                               section_description=section.descrizione,
                                                                                               section_content=section.contenuto,
                                                                                               previous_queries_list=previous_search_queries,
                                                                                               number_of_queries=configurable.number_of_queries,
                                                                                               json_format=Queries.model_json_schema()
                                                                                               )
            planner_provider = get_config_value(configurable.planner_provider)
            planner_model = get_config_value(configurable.planner_model)
            reflection_model = llm_provide(planner_model, planner_provider)
            results = reflection_model.invoke([SystemMessage(content=section_grader_instructions_formatted),
                                               HumanMessage(
                                                   content="Genera query di approfondimento per migliorare la sezione del report.")])

            new_queries: Queries = parse_model(Queries, results.content)

            return Command(
                update={"search_queries": new_queries.queries, "section": section},
                goto=SearchWebAgent.Name
            )
        else:
            section_writer_inputs_formatted = section_writer_instructions_review.format(topic=topic,
                                                                                        report_structure=report_structure,
                                                                                        section_number=section_number,
                                                                                        total_sections=len(state.all_sections),
                                                                                        section_title=section.nome,
                                                                                        section_description=section.descrizione,
                                                                                        section_content=section.contenuto,
                                                                                        numero_prima_fonte = most_recent_web_research[0]["num_source"],
                                                                                        new_sources=formatted_sources,
                                                                                        previous_queries_list=previous_search_queries,
                                                                                        number_of_followup_queries=configurable.number_of_queries,
                                                                                        json_format=SectionReview.model_json_schema()
                                                                                        )
            results = writer_model.invoke([SystemMessage(content=section_writer_inputs_formatted),
                                                   HumanMessage(content="Arricchisci il contenuto della sezione con le nuove fonti ed esprimi un giudizio se continuare la ricerca oppure passare il nuovo contenuto generato.")])
            try:
                section_review: SectionReview = parse_model(SectionReview, results.content)
            except Exception as e:
                print("ERROR PARSING SECTION REVIEW -----------------")
                print(results.content)  # todo: remove
                print("---------------------------- -----------------")
                raise

            section.contenuto = section_review.new_section_content
            if section_review.grade.upper() == "PASS"  or state.search_iterations >= configurable.max_search_depth:
                section.sources = sum(state.web_research_results, [])
                #todo: elimnare full content da sources
                for source in section.sources:
                    source['full_content'] = ""
                return Command(
                    update={"completed_sections": [section]}, goto=END)
            else:
                return Command(
                    update={"search_queries": section_review.follow_up_queries, "section": section},
                    goto=SearchWebAgent.Name
                )
