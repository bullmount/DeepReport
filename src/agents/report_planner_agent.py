import os
from typing import Dict

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from configuration import Configuration
from deep_report_state import DeepReportState, Queries, Sections
from prompts import report_planner_query_writer_instructions, report_planner_instructions
from search_system import SearchSystem
from utils.json_extractor import parse_model
from utils.llm_provider import llm_provide
from utils.sources_formatter import SourcesFormatter
from utils.utils import get_config_value
from langchain.chat_models import init_chat_model
from  pathlib import Path

class ReportPlannerAgent():
    def __init__(self, ):
        pass

    def invoke(self, state: DeepReportState, config: RunnableConfig) -> Dict[str, any]:
        topic = state.topic
        feedback = state.feedback_on_report_plan

        file_path = Path("sections.json")
        if not feedback and  file_path.exists():
            data = file_path.read_text(encoding="utf-8")
            sections_loaded = Sections.model_validate_json(data)
            return {"sections": sections_loaded.sezioni}

        configurable = Configuration.from_runnable_config(config)

        # return {"sections": [], "final_report": "no final report"}

        report_structure = configurable.report_structure
        number_of_queries = configurable.number_of_queries
        search_api = get_config_value(configurable.search_api)
        # params_to_pass = get_search_params(search_api, search_api_config)  # Filter parameters

        # Convert JSON object to string if necessary
        if isinstance(report_structure, dict):
            report_structure = str(report_structure)

        # Set writer model (model used for query writing)
        writer_provider = get_config_value(configurable.writer_provider)
        writer_model_name = get_config_value(configurable.writer_model)
        structured_llm = llm_provide(writer_model_name, writer_provider, max_tokens=1000)

        # Format system instructions
        system_instructions_query = report_planner_query_writer_instructions.format(topic=topic,
                                                                                    json_format=Queries.model_json_schema(),
                                                                                    report_organization=report_structure,
                                                                                    number_of_queries=number_of_queries)

        # Generate queries
        results = structured_llm.invoke([SystemMessage(content=system_instructions_query),
                                         HumanMessage(
                                             content="Genera query di ricerca che aiutino a pianificare le sezioni del report.")])
        queries: Queries = parse_model(Queries, results.content)

        # Web search
        query_list = [query.search_query for query in queries.queries]

        # Search the web with parameters
        search_sys = SearchSystem(configurable.search_api)
        sources = search_sys.execute_search(query_list, max_filtered_results=4, max_results_per_query=4,
                                            include_raw_content=True, exclude_sources=[])
        sources_formatter = SourcesFormatter()
        source_str = sources_formatter.format_sources(sources,
                                                      include_raw_content=True,
                                                      max_tokens_per_source=1000,
                                                      numbering=False)

        # Format system instructions
        system_instructions_sections = report_planner_instructions.format(topic=topic,
                                                                          report_organization=report_structure,
                                                                          context=source_str, feedback=feedback,
                                                                          json_format=Sections.model_json_schema())

        # Set the planner
        planner_provider = get_config_value(configurable.planner_provider)
        planner_model = get_config_value(configurable.planner_model)

        # Report planner instructions
        planner_message = """Genera le sezioni del report. La tua risposta deve includere un campo 'sections' contenente un elenco di sezioni.
Ogni sezione deve avere i campi: nome, descrizione, piano, ricerca e contenuto."""

        planner_llm = llm_provide(planner_model, planner_provider, max_tokens=6000)

        # Generate the report sections
        report_sections = planner_llm.invoke([SystemMessage(content=system_instructions_sections),
                                              HumanMessage(content=planner_message)])

        sections: Sections = parse_model(Sections, report_sections.content)

        # todo: remove
        output_path = Path("sections.json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sections.model_dump_json(indent=4))

        return {"sections": sections.sezioni}
