from dataclasses import dataclass, field
from typing_extensions import Annotated
import operator
from pydantic import BaseModel, Field
from typing import Annotated, List, TypedDict, Literal


# todo: spostare

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")


class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )


class Section(BaseModel):
    nome: str = Field(
        description="Nome per questa sezione del report.",
    )
    descrizione: str = Field(
        description="Breve panoramica degli argomenti e concetti principali che saranno trattati in questa sezione.",
    )
    ricerca: bool = Field(
        description="Se è necessario effettuare ricerche web per questa sezione del report."
    )
    contenuto: str = Field(
        description="Contenuto della sezione."
    )


class Sections(BaseModel):
    sezioni: List[Section] = Field(
        description="Sezioni del report.",
    )

class Feedback(BaseModel):
    grade: Literal["pass","fail"] = Field(
        description="Risultato della valutazione che indica se la risposta soddisfa i requisiti ('pass') o necessita di revisione ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="Elenco delle query di ricerca di approfondimento.",
    )

# -------------------------------------------------------------------------------------

@dataclass(kw_only=True)
class DeepReportStateInput():
    topic: str = field(default=None)


@dataclass(kw_only=True)
class DeepReportStateOutput():
    final_report: str = field(default=None)


@dataclass(kw_only=True)
class DeepReportState():
    topic: str = field(default=None)
    feedback_on_report_plan: str = field(default=None)
    final_report: str = field(default=None)
    sections: list[Section] = field(default=None)  # List of report sections
    completed_sections: Annotated[list, operator.add]  # Send() API key


@dataclass(kw_only=True)
class SectionState():
    topic: str = field(default=None)  # Report topic
    section: Section = field(default=None)  # Report section
    search_iterations: int = field(default=0)  # Number of search iterations done
    search_queries: list[SearchQuery] = field(default=None)  # List of search queries
    source_str: str = field(default=None)  # String of formatted source content from web search
    report_sections_from_research: str = field(
        default=None)  # String of any completed sections from research to write final sections


@dataclass(kw_only=True)
class SectionOutputState(TypedDict):
    completed_sections: list[Section] = field(default=None)
