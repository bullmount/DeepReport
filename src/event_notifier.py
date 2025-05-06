import requests
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, TypedDict, List
import logging
from datetime import datetime
import json
from enum import IntEnum

from deep_report_state import SectionState


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class ProcessState(IntEnum):
    NotStarted = 0,
    Started = 1,
    Searching = 2,
    Planning = 3,
    WaitingForApproval = 4,
    Approved=5,
    WritingSection = 6,
    Reviewing = 7,
    Canceled = 8,
    Completed = 9,
    #----
    Aborted = 10,
    Error = 11


@dataclass
class EventData:
    event_type: str
    message: str
    state: int = None
    timestamp: datetime = None
    # severity: str = "INFO"
    data: Optional[dict] = None

    def to_json(self) -> str:
        dict_data = asdict(self)
        dict_data['timestamp'] = datetime.now().isoformat()
        return json.dumps(dict_data, cls=CustomJSONEncoder)

    def to_dict(self) -> dict:
        """Converte l'oggetto in dizionario"""
        dict_data = asdict(self)
        dict_data['timestamp'] = datetime.now().isoformat()
        dict_data['data'] = json.dumps(self.data, cls=CustomJSONEncoder)
        return dict_data

class FaseSezione(IntEnum):
    QUERY=0,
    SEARCH=1,
    WRITE=2,
    COMPLETE=3


class SectionData(TypedDict):
    sezione_posizione: int
    sezione_nome: str
    search_iterations: int
    search_queries: List[str]
    fase:FaseSezione


def LoadSectionData(state: SectionState, fase:FaseSezione) -> SectionData:
    return SectionData(sezione_posizione=state.section.posizione,
                       sezione_nome=state.section.nome,
                       fase=fase,
                       search_iterations=state.search_iterations,
                       search_queries= [q.search_query for q in state.search_queries] if state.search_queries else [])


class EventNotifier:
    def __init__(self, base_url: str = "http://localhost:5285"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/api/DeepReportApi/SendEvent"
        self.logger = logging.getLogger(__name__)

    def send_message(self, message: EventData) -> Optional[Dict[Any, Any]]:
        try:
            response = requests.post(url=self.endpoint, json=message.to_dict())
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Errore nell'invio del messaggio: {e}")
            return None

    def is_server_available(self) -> bool:
        """Verifica se il server è raggiungibile"""
        try:
            response = requests.get(f"{self.base_url}/api/DeepReportApi/health")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


