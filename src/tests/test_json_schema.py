from pydantic import BaseModel, Field
from typing import List
import json

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")

class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )

# Verifica quale versione di Pydantic stai usando
try:
    # Pydantic v2
    json_schema = Queries.model_json_schema()
except AttributeError:
    # Pydantic v1
    json_schema = Queries.schema()

# Formatta il JSON in modo leggibile
formatted_schema = json.dumps(json_schema, indent=2)
print(formatted_schema)