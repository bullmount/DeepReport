from typing import Dict
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from deep_report_state import SectionState
from search_system import SearchSystem
from utils.sources_formatter import SourcesFormatter


class SearchWebAgent():
    Name: str = "search_web"

    def __init__(self):
        pass

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        search_queries = state.search_queries
        prev_web_research_results = sum(state.web_research_results, [])
        configurable = Configuration.from_runnable_config(config)

        query_list = [query.search_query for query in search_queries]
        search_sys = SearchSystem(configurable.search_api)
        sources = search_sys.execute_search(query_list, max_filtered_results=4, max_results_per_query=4,
                                            include_raw_content=True,
                                            sites=configurable.sites_search_restriction,
                                            exclude_sources=prev_web_research_results)

        sources_formatter = SourcesFormatter()
        source_str = sources_formatter.format_sources(sources,
                                                      include_raw_content=True,
                                                      max_tokens_per_source=3000,
                                                      numbering=False)

        return {
            "source_str": source_str,
            "search_iterations": state.search_iterations + 1,
            "web_research_results": [sources]
        }
