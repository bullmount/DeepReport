from typing import Optional

from pydantic import BaseModel


class ResearchResponse(BaseModel):
    topic: Optional[str] = ""
    message: Optional[str] = ""
    success:bool


class AbortResponse(BaseModel):
    message: Optional[str] = ""
    success:bool
