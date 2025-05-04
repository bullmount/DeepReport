from dataclasses import dataclass, field
from typing_extensions import Annotated
import operator
from pydantic import BaseModel, Field
from typing import Annotated, List, TypedDict, Literal, Optional

from search_engines.search_engine_base import SearchEngResult


# todo: spostare

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query per la ricerca web.")


class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="Liste delle query per la ricerca web.",
    )


class Section(BaseModel):
    posizione:int = Field(
        description="posizione della sezione a partire da 1.",default=1
    )
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
    tipo: Literal["introduzione", "conclusioni", "confronto", "standard"] = Field(
        description='Tipo di sezione'
    )
    sources: List[SearchEngResult] = Field(description="Fonti usate in sezione.", default_factory=list)


class Tematica(BaseModel):
    titolo: str = Field(description="Titolo della tematica.", )
    descrizione: str = Field(description="Breve descrizione della tematica.", )


class Sections(BaseModel):
    tematiche: List[Tematica] = Field(description="Tematiche del report.", default_factory=list)
    sezioni: List[Section] = Field(
        description="Sezioni del report.",
    )


class Feedback(BaseModel):
    grade: Literal["pass", "fail"] = Field(
        description="Risultato della valutazione che indica se la risposta soddisfa i requisiti ('pass') o necessita di revisione ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="Elenco delle query di ricerca di approfondimento."
    )


# lo schema non riporta le descrizioni
class SectionReview(BaseModel):
    new_section_content: str = Field(description="Contenuto arricchito della sezione")
    grade: Literal["RESEARCH", "PASS"] = Field(
        description='Giudizio se occorre nuova ricerca web (RESEARCH) o passare il contenuto (PASS).')
    follow_up_queries: List[SearchQuery] = Field(
        description="Elenco delle query di ricerca di approfondimento (solo se giudizio è RESEARCH).")


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
    queries: Queries = field(default=None)
    feedback_on_report_plan: str = field(default=None)
    final_report: str = field(default=None)
    themes: list[Tematica] = field(default=None)
    sections: list[Section] = field(default=None)  # List of report sections
    completed_sections: Annotated[list, operator.add]  # Send() API key
    report_sections_from_research: str = field(default=None)
    bad_search_results: Annotated[list, operator.add] = field(default_factory=list)

    final_report: str = field(default=None)  # Final report


@dataclass(kw_only=True)
class SectionState:
    topic: str = field(default=None)
    all_sections: list[Section] = field(default=None)
    section: Section = field(default=None)
    search_iterations: int = field(default=0)
    search_queries: list[SearchQuery] = field(default=None)
    previous_search_queries: Annotated[list[SearchQuery], operator.add] = field(default_factory=list[SearchQuery])
    report_sections_from_research: str = field(default=None)
    completed_sections: list[Section] = field(default=None)
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    bad_search_results: Annotated[list, operator.add] = field(default_factory=list)


@dataclass(kw_only=True)
class SectionOutputState(TypedDict):
    completed_sections: list[Section] = field(default=None)
