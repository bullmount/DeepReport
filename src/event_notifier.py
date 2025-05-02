import requests
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import json
from enum import IntEnum
import time


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
    Writing = 5,
    Reviewing = 6,
    Canceled = 7,
    Completed = 8,
    Aborted = 9,
    Error = 10

@dataclass
class EventData:
    event_type: str
    message: str
    state:int = None
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


# @dataclass
# class EventNotifierMessage:
#     user: str
#     text: str


class EventNotifier:
    def __init__(self, base_url: str = "http://localhost:5285"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/api/DeepReportApi/SendEvent"
        self.logger = logging.getLogger(__name__)

    def send_message(self, message: EventData) -> Optional[Dict[Any, Any]]:
        try:
            # print("send message")
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


if __name__ == "__main__":
    # Configurazione logging
    logging.basicConfig(level=logging.INFO)

    # Creazione client
    client = EventNotifier()

    data ={"sezioni": [
        {"titolo": "titolo1", "descrizione": "descr 1", "richiede_ricerca": True},
        {"titolo": "titolo2", "descrizione": "descr 2", "richiede_ricerca": False},
    ]}

    # Verifica disponibilità server
    if client.is_server_available():
        message = EventData(event_type="INFO", message="ciao", state=ProcessState.Started, data=data)
        response = client.send_message(message)
        time.sleep(1)
        # Creazione e invio messaggio
        message = EventData(event_type="INFO",message="ciao", state=ProcessState.WaitingForApproval, data=data)
        response = client.send_message(message)

        if response:
            print("✅ Risposta dal server Blazor:", response)
    else:
        print("❌ Server non raggiungibile")
