from typing import List, Optional, ClassVar
from search_engines.search_engine_base import BaseSearchEngine, SearchEngResult
import threading
import uuid
from tavily import TavilyClient
import os
import logging
import time

logger = logging.getLogger(__name__)


class TavilySearchEngine(BaseSearchEngine):
    _last_search_time: ClassVar[float] = 0.0
    _min_delay: ClassVar[float] = 1.0
    _delay_lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self):
        super().__init__(name="Tavily")

    @classmethod
    def _ensure_delay(cls) -> None:
        with cls._delay_lock:
            """Metodo di classe per gestire il delay tra le ricerche"""
            current_time = time.time()
            elapsed = current_time - cls._last_search_time

            if elapsed < cls._min_delay:
                time.sleep(cls._min_delay - elapsed)

            cls._last_search_time = time.time()

    def search(self, query, max_results: Optional[int] = 10, sites: List[str] = None) -> List[SearchEngResult]:
        # Applica il rate limiting a livello di classe
        self._ensure_delay()

        results: List[SearchEngResult] = []
        try:
            tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

            search_results = tavily_client.search(query,
                                                  include_domains=[] if sites is None else sites,
                                                  max_results=max_results,
                                                  include_raw_content=False)
            k = 0
            for res in search_results:
                url = res.get('url')
                title = res.get('title')
                content = res.get('content')
                k += 1
                if not all([url, title, content]):
                    logger.warning(f"Warning: Incomplete result from Google: {res}")
                    continue
                results.append(
                    SearchEngResult(id=str(uuid.uuid4()), query=query, title=title, snippet=content, url=url,
                                    position=k,
                                    full_content=None, num_source=None, score=None, search_engine=self.name))
        except Exception as e:
            logger.error(f"Error searching Google: {str(e)}")
        return results
