from typing import Dict
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

from agents.agent_base import DeepReportAgentBase, EventData
from configuration import Configuration
from deep_report_state import DeepReportState, Queries, Sections
from event_notifier import ProcessState
from prompts import report_planner_query_writer_instructions, report_planner_instructions_initial, \
    report_planner_query_writer_with_feedback_instructions, \
    report_planner_instructions_with_feedback_and_additional_section
from search_system import SearchSystem
from utils.json_extractor import parse_model
from utils.llm_provider import llm_provide
from utils.sources_formatter import SourcesFormatter
from utils.utils import get_config_value, get_current_date, estrai_sezioni_markdown_e_indice_assegnata
from pathlib import Path


class ReportPlannerAgent(DeepReportAgentBase):
    Name = "generate_report_plan"

    def __init__(self):
        super().__init__()

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    @time_tracker
    def invoke(self, state: DeepReportState, config: RunnableConfig) -> Dict[str, any]:
        topic = state.topic
        feedback = state.feedback_on_report_plan

        configurable = Configuration.from_runnable_config(config)
        report_structure = configurable.report_structure
        number_of_queries = configurable.number_of_queries

        search_sys = SearchSystem(configurable.search_api)
        sources_formatter = SourcesFormatter()

        # --------------------------------------------------
        # file_path_1 = Path("sections.json")
        # file_path_2 = Path("queries.json")
        # if not feedback and file_path_1.exists() and file_path_2.exists():
        #     data = file_path_1.read_text(encoding="utf-8")
        #     sections_loaded = Sections.model_validate_json(data)
        #     data = file_path_2.read_text(encoding="utf-8")
        #     queries_loaded = Queries.model_validate_json(data)
        #     return {"queries": queries_loaded, "themes": sections_loaded.tematiche, "sections": sections_loaded.sezioni}
        # --------------------------------------------------

        if isinstance(report_structure, dict):
            report_structure = str(report_structure)

        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)
        structured_llm = llm_provide(writer_model_name, writer_provider, max_tokens=3000)

        current_date = get_current_date()

        self.event_notify(event_data=EventData(event_type="INFO",
                                               state=ProcessState.Searching,
                                               message="Pre ricerca per focalizzare le query"))

        sources, bad_urls = search_sys.execute_search([topic],
                                                      max_filtered_results=configurable.max_results_per_query * 2,
                                                      max_results_per_query=configurable.max_results_per_query * 2,
                                                      include_raw_content=False,  # nella pre ricerca [include_raw_content = False]
                                                      exclude_sources=state.bad_search_results)
        starting_knowledge = sources_formatter.format_sources(sources, include_raw_content=False,
                                                              max_tokens_per_source=1000, numbering=False)

        self.event_notify(event_data=EventData(event_type="INFO",
                                               state=ProcessState.Searching,
                                               message="Determinazione query di ricerca"))

        if feedback is None:  # query per la prima pianificazione
            system_instructions_query = report_planner_query_writer_instructions.format(topic=topic,
                                                                                        current_date=current_date,
                                                                                        starting_knowledge=starting_knowledge,
                                                                                        json_format=Queries.model_json_schema(),
                                                                                        number_of_queries=number_of_queries)

            results = structured_llm.invoke([SystemMessage(content=system_instructions_query),
                                             HumanMessage(
                                                 content="Genera query di ricerca che aiutino a pianificare le sezioni del report.")],
                                            response_format=Queries.model_json_schema())
            queries: Queries = parse_model(Queries, results.content)
        else:   # query per revisione della pianificazione
            _, proposed_structure = estrai_sezioni_markdown_e_indice_assegnata(state.sections, None,
                                                                               include_assegnata=True)
            system_instructions_query = report_planner_query_writer_with_feedback_instructions.format(topic=topic,
                                                                                                      current_date=current_date,
                                                                                                      starting_knowledge=starting_knowledge,
                                                                                                      proposed_structure=proposed_structure,
                                                                                                      user_feedback=feedback,
                                                                                                      number_of_queries=number_of_queries,
                                                                                                      json_format=Queries.model_json_schema()
                                                                                                      )
            results = structured_llm.invoke([SystemMessage(content=system_instructions_query),
                                             HumanMessage(
                                                 content="Genera query di ricerca che aiutino a pianificare le sezioni del report.")],
                                            response_format=Queries.model_json_schema())
            queries: Queries = parse_model(Queries, results.content)

        query_list = [state.topic]
        query_list.extend([query.search_query for query in queries.queries])

        self.event_notify(event_data=EventData(event_type="INFO",
                                               state=ProcessState.Searching,
                                               message="Ricerca contenuti su web"))

        sources, bad_urls = search_sys.execute_search(query_list,
                                                      max_filtered_results=configurable.max_results_per_query,
                                                      max_results_per_query=configurable.max_results_per_query,
                                                      include_raw_content=configurable.fetch_full_page,
                                                      sites=configurable.sites_search_restriction,
                                                      exclude_sources=state.bad_search_results)

        source_str = sources_formatter.format_sources(sources,
                                                      include_raw_content=True,
                                                      max_tokens_per_source=1000,
                                                      numbering=False)

        planner_provider = get_config_value(configurable.planner_provider)
        planner_model = get_config_value(configurable.planner_model)

        self.event_notify(event_data=EventData(event_type="INFO",
                                               state=ProcessState.Planning,
                                               message="Pianificazione sezioni del report."))

        if feedback is None:  # prima pianificazione
            system_instructions_sections = report_planner_instructions_initial.format(topic=topic,
                                                                                      report_organization=report_structure,
                                                                                      context=source_str,
                                                                                      json_format=Sections.model_json_schema())

            planner_message = """Pianifica le sezioni che devono comporre il report.
    La tua risposta deve includere un campo 'sezioni' contenente un elenco di sezioni e un campo 'tematiche' contenente l'elenco delle tematiche importanti sul report.
    Ogni sezione deve avere i campi: nome, descrizione, piano, indicatore se richiede ricerca, contenuto e tipo.
    Orni tematica deve avere i campi: titolo e descrizione."""
            planner_llm = llm_provide(planner_model, planner_provider, max_tokens=6000)
            result_sections = planner_llm.invoke([SystemMessage(content=system_instructions_sections),
                                                  HumanMessage(content=planner_message)],
                                                 response_format=Sections.model_json_schema())
        else:
            _, proposed_structure = estrai_sezioni_markdown_e_indice_assegnata(state.sections, None,
                                                                               include_assegnata=True)
            system_instructions_sections = report_planner_instructions_with_feedback_and_additional_section.format(
                topic=topic,
                report_organization=proposed_structure,
                user_feedback=feedback,
                context=source_str,
                json_format=Sections.model_json_schema())
            planner_message = """Pianifica le sezioni che devono comporre il report considerado il feedback dell'utente.
                La tua risposta deve includere un campo 'sezioni' contenente un elenco di sezioni e un campo 'tematiche' contenente l'elenco delle tematiche importanti sul report.
                Ogni sezione deve avere i campi: nome, descrizione, piano, indicatore se richiede ricerca, contenuto e tipo.
                Ogni tematica deve avere i campi: titolo e descrizione."""
            planner_llm = llm_provide(planner_model, planner_provider, max_tokens=6000)
            result_sections = planner_llm.invoke([SystemMessage(content=system_instructions_sections),
                                                  HumanMessage(content=planner_message)],
                                                 response_format=Sections.model_json_schema())

        sections: Sections = parse_model(Sections, result_sections.content)

        section_pos = 0
        for s in sections.sezioni:
            section_pos = section_pos + 1
            s.posizione = section_pos

        # --------------------
        # output_path = Path("sections.json")
        # with open(output_path, "w", encoding="utf-8") as f:
        #     f.write(sections.model_dump_json(indent=4))
        #
        # output_path = Path("queries.json")
        # with open(output_path, "w", encoding="utf-8") as f:
        #     f.write(queries.model_dump_json(indent=4))
        # --------------------

        return {"queries": queries, "themes": sections.tematiche,
                "bad_search_results": bad_urls,
                "sections": sections.sezioni}
