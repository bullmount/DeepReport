from abc import ABC, abstractmethod


from event_notifier import EventNotifier,  EventData
import logging

logger = logging.getLogger(__name__)


class DeepReportAgentBase(ABC):
    def __init__(self):
        self._event_notifier = EventNotifier()
        pass


    def event_notify(self, event_data: EventData) -> None:
        try:
            # json_data = event_data.to_json()
            # print(json_data)
            self._event_notifier.send_message(event_data)
        except Exception as e:
            logger.error(f"Errore durante la notifica dell'evento: {e}")
