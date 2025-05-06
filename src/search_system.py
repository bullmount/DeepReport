import math
from typing import Optional, List, Tuple
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer, util  # Importa SentenceTransformer

import logging

from sentence_transformers import SentenceTransformer

from configuration import SearchAPI
from search_engines.search_engine_base import SearchEngResult, BaseSearchEngine
from search_engines.search_engine_ddg import DuckDuckGoSearchEngine
from search_engines.search_engine_google import GoogleSearchEngine
import ssl
from requests.adapters import HTTPAdapter
import threading
import torch

from threading import Lock
from typing import ClassVar, Dict

from search_engines.search_engine_tavily import TavilySearchEngine
from utils.url_fetcher import UrlFetcher

logger = logging.getLogger(__name__)

lock = threading.Lock()


class SSLIgnoreAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False  # ❗️DISATTIVA PRIMA
        context.verify_mode = ssl.CERT_NONE  # ❗️POI IMPOSTA verify_mode
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


class SearchSystem:
    _embedding_lock: ClassVar[Lock] = threading.Lock()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    _embedding_model: ClassVar[SentenceTransformer] = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2", trust_remote_code=True)
    _embedding_model.to(device=device)

    def __init__(self, search_api: SearchAPI):
        self._search_api = search_api

    @time_tracker
    def execute_search(self, query_list: list[str],
                       max_filtered_results: int,
                       max_results_per_query: int,
                       include_raw_content: bool = False,
                       exclude_sources: Optional[List[SearchEngResult]] = None,
                       sites: Optional[List[str]] = None,
                       additional_params=None) -> Tuple[List[SearchEngResult],List[SearchEngResult]]:

        bad_urls = []
        search_engine: BaseSearchEngine = self._create_search_engine()

        all_results: List[SearchEngResult] = []
        exclude_sources = exclude_sources or []

        num_queries = len(query_list)
        num_exclusions = len(exclude_sources)
        if num_exclusions > 0:
            delta_per_query = math.ceil(num_exclusions / num_queries)
            max_results_per_query2 = max_results_per_query + delta_per_query
        else:
            max_results_per_query2 = max_results_per_query

        for query in query_list:
            all_query_results: List[SearchEngResult] = search_engine.search(query,
                                                                            max_results=max_results_per_query2,
                                                                            sites=sites)
            filtered_results = [r for r in all_query_results
                                if not any(exclude_result['url'] == r['url'] for exclude_result in exclude_sources)]

            filtered_results = filtered_results[:max_results_per_query]

            for r in filtered_results:
                r['query'] = query
                r['search_engine'] = self._search_api.value
                r['full_content'] = ""
            all_results.extend(filtered_results)

        if include_raw_content:
            url_set = set()
            for r in all_results:
                url_set.add(r['url'])

            url_loader = UrlFetcher()
            processed_results = url_loader.fetch_contents(list(url_set))

            for r in all_results:
                r['full_content'] = processed_results[r['url']]

            bad_urls =  [r for r in all_results if
                           r['full_content'] is not None and len(r['full_content'].split()) <= 80]

            all_results = [r for r in all_results if
                           r['full_content'] is not None and len(r['full_content'].split()) > 80]

        if len(all_results) <= 1:
            return all_results, bad_urls

        for x in all_results:
            if len(x["snippet"]) == 0:
                x["snippet"] = "nessuna descrizione"

        top_results = self._rank_search_results(all_results, max_filtered_results, include_raw_content)
        return top_results[:max_filtered_results], bad_urls

    def _create_search_engine(self) -> BaseSearchEngine:
        if self._search_api == SearchAPI.GOOGLESEARCH:
            return GoogleSearchEngine()
        elif self._search_api == SearchAPI.DUCKDUCKGO:
            return DuckDuckGoSearchEngine()
        elif self._search_api == SearchAPI.TAVILY:
            return TavilySearchEngine()
        else:
            raise ValueError("Invalid search engine name")


    @staticmethod
    def _rank_search_results(results: List[SearchEngResult], top_n: int,
                             include_raw_content: bool) -> List[SearchEngResult]:
        df = pd.DataFrame(results)
        df['desc_length'] = df['snippet'].str.len()

        # 1. Calcola gli embedding per snippet e query
        with SearchSystem._embedding_lock:
            snippet_embeddings = SearchSystem._embedding_model.encode(df['snippet'].tolist())
            query_embeddings = SearchSystem._embedding_model.encode(df['query'].tolist())

        # 2. Calcola la similarità coseno tra ogni snippet e la sua query corrispondente
        df['semantic_similarity'] = [util.pytorch_cos_sim(s_emb, q_emb).item()
                                     for s_emb, q_emb in zip(snippet_embeddings, query_embeddings)]

        numeric_cols = ['position', 'desc_length',
                        # 'semantic_similarity'
                        ]
        if include_raw_content:
            df['page_length'] = df['full_content'].str.len()
            numeric_cols.append('page_length')

        url_counts = Counter(df['url'])
        df['url_frequency'] = df['url'].map(url_counts)

        scaler = MinMaxScaler()
        df_scaled = df.copy()

        if not df[numeric_cols].empty:
            df_scaled[numeric_cols] = scaler.fit_transform(df[numeric_cols])

        max_freq = df['url_frequency'].max()
        df_scaled['url_frequency_norm'] = df['url_frequency'] / max_freq if max_freq > 0 else 0

        # 3.1 Inverti il valore della posizione (rank più basso è migliore)
        df_scaled['position_score'] = 1 - df_scaled['position']

        # 3.2 Calcola punteggio per lunghezza descrizione (preferibilmente non troppo corta né troppo lunga)
        # Questo crea una curva a campana con picco a 0.5
        df_scaled['desc_length_score'] = 1 - 2 * np.abs(df_scaled['desc_length'] - 0.5)

        # 3.3 Punteggio per similarità semantica
        df_scaled['semantic_score'] = df_scaled['semantic_similarity']

        if include_raw_content:
            # 3.4 Calcola punteggio per lunghezza pagina
            # Assumiamo che pagine più lunghe abbiano più contenuto, ma non troppo lunghe
            df_scaled['page_length_score'] = np.where(
                df_scaled['page_length'] <= 0.7,
                df_scaled['page_length'],
                0.7 - 0.3 * (df_scaled['page_length'] - 0.7) / 0.3
            )

            # 4. Calcolo dello score composito con pesi
            # Ora includiamo la frequenza dell'URL tra le query
            df_scaled['final_score'] = (
                    0.3 * df_scaled['position_score'] +  # Leggermente meno peso alla posizione
                    0.2 * df_scaled['page_length_score'] +  # La lunghezza della pagina rimane importante
                    0.1 * df_scaled['desc_length_score'] +  # Meno peso alla lunghezza della descrizione
                    0.3 * df_scaled['semantic_score'] +  # Importante peso alla similarità semantica
                    0.1 * df_scaled['url_frequency_norm']  # Leggermente meno peso alla frequenza dell'URL
            )
        else:
            df_scaled['final_score'] = (
                    0.4 * df_scaled['position_score'] +  # La posizione originale diventa più importante
                    0.2 * df_scaled['desc_length_score'] +  # La lunghezza della descrizione resta importante
                    0.3 * df_scaled['semantic_score'] +  # Importante peso alla similarità semantica
                    0.1 * df_scaled['url_frequency_norm']  # Premiamo di più i risultati che appaiono in più query
            )

        unique_urls = []
        final_indices = []

        for idx in df_scaled.sort_values('final_score', ascending=False).index:
            url = df_scaled.loc[idx, 'url']
            # Se l'URL non è già stato selezionato, lo aggiungiamo
            if url not in unique_urls:
                unique_urls.append(url)
                final_indices.append(idx)
                # Ci fermiamo quando raggiungiamo il numero desiderato di risultati
                if len(unique_urls) >= top_n:
                    break

        assert final_indices
        final_result_df = df.loc[final_indices].copy()
        final_result_df['score'] = df_scaled.loc[final_indices, 'final_score']
        final_result_df['frequency'] = df.loc[final_indices, 'url_frequency']
        final_result_df['semantic_similarity'] = df_scaled.loc[final_indices, 'semantic_similarity']
        search_results: List[SearchEngResult] = []
        for idx, row in final_result_df.iterrows():
            # Crea un dizionario con tutti i valori
            result_dict = {}

            # Itera su tutte le chiavi del DataFrame
            for key in SearchEngResult.__annotations__.keys():
                # Assegna il valore dalla riga corrente
                result_dict[key] = row[key]
            result_dict['score'] = row['score']

            # Crea l'oggetto SearchEngResult dal dizionario
            result = SearchEngResult(**result_dict)
            search_results.append(result)

        search_results.sort(key=lambda x: x['score'], reverse=True)

        return search_results
