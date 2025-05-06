import os
from enum import Enum
from dataclasses import dataclass, fields
from typing import Any, Optional, Dict, List

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass


DEFAULT_REPORT_STRUCTURE = """Usa questa struttura per creare un report sull'argomento fornito dall'utente:

1. Introduzione (nessuna ricerca necessaria)
   - Breve panoramica dell'area tematica che introduce i temi trattai nelle sezioni successive

2. Sezioni principali:
   - Ogni sezione deve concentrarsi su un sotto-argomento relativo al tema fornito, e deve essere approfondita con ricerche sul web.

3. Conclusione  (nessuna ricerca necessaria)
   - Inserisci un solo elemento strutturale (una lista oppure una tabella) che sintetizzi le sezioni principali
   - Fornisci un riassunto conciso del report"""


class SearchAPI(Enum):
    TAVILY = "tavily"
    # ARXIV = "arxiv"
    # PUBMED = "pubmed"
    # LINKUP = "linkup"
    DUCKDUCKGO = "duckduckgo"
    GOOGLESEARCH = "googlesearch"


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    report_structure: str = DEFAULT_REPORT_STRUCTURE # Defaults to the default report structure
    number_of_queries: int = 2 # default(2) Number of search queries to generate per iteration
    max_results_per_query:int = 4
    max_search_depth: int = 2 # default(2) Maximum number of reflection + search iterations

    search_api: SearchAPI = SearchAPI.GOOGLESEARCH # Default to GOOGLE
    search_api_config: Optional[Dict[str, Any]] = None
    sites_search_restriction:Optional[List[str]] = None
    fetch_full_page:bool = False

    planner_provider: str = "openrouter"  # Defaults to Anthropic as provider
    planner_model: str = "mistralai/mistral-small-24b-instruct-2501:free" # Defaults to claude-3-7-sonnet-latest
    writer_provider: str = "openrouter" # Defaults to Anthropic as provider
    writer_model: str = "mistralai/mistral-small-24b-instruct-2501:free" # Defaults to claude-3-5-sonnet-latest

    @classmethod
    def from_runnable_config(
            cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})