from pydantic import BaseModel

from configuration import SearchAPI


class ResearchRequestConfig(BaseModel):
    number_of_queries:int
    max_search_depth:int
    max_results_per_query:int
    search_api:SearchAPI
    fetch_full_page:bool


class ResearchRequest(BaseModel):
    topic: str
    config: ResearchRequestConfig


class FeedbackRequest(BaseModel):
    feedback:str