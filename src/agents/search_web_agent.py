from typing import Dict
from langchain_core.runnables import RunnableConfig

from agents.agent_base import DeepReportAgentBase, EventData
from configuration import Configuration
from deep_report_state import SectionState
from event_notifier import ProcessState, LoadSectionData, FaseSezione
from search_system import SearchSystem
from utils.traccia_tempo import time_tracker


class SearchWebAgent(DeepReportAgentBase):
    Name: str = "search_web"

    def __init__(self):
        super().__init__()

    @classmethod
    def node(cls):
        return cls.Name, cls().invoke

    @time_tracker
    def invoke(self, state: SectionState, config: RunnableConfig) -> Dict[str, any]:
        self.event_notify(event_data=EventData(event_type="INFO",
                                               state=ProcessState.WritingSection,
                                               message=f"Ricerca contenuti web",
                                               data=dict(LoadSectionData(state, FaseSezione.SERACH))))

        search_queries = state.search_queries
        prev_web_research_results = sum(state.web_research_results, [])
        prev_web_research_results.extend(state.bad_search_results)
        last_num_source = len(prev_web_research_results)
        configurable = Configuration.from_runnable_config(config)

        query_list = [query.search_query for query in search_queries]
        search_sys = SearchSystem(configurable.search_api)
        sources, bad_urls = search_sys.execute_search(query_list,
                                                      max_filtered_results=configurable.max_results_per_query,
                                                      max_results_per_query=configurable.max_results_per_query,
                                                      include_raw_content=configurable.fetch_full_page,
                                                      sites=configurable.sites_search_restriction,
                                                      exclude_sources=prev_web_research_results)
        for res in sources:
            last_num_source += 1
            res['num_source'] = last_num_source

        # todo: remove
        # sources_formatter = SourcesFormatter()
        # source_str = sources_formatter.format_sources(sources,
        #                                               include_raw_content=True,
        #                                               max_tokens_per_source=3000,
        #                                               numbering=False)
        return {
            "search_iterations": state.search_iterations + 1,
            "previous_search_queries": search_queries,
            "web_research_results": [sources],
            "bad_search_results": bad_urls
        }
