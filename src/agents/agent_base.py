from abc import ABC, abstractmethod


from event_notifier import EventNotifier,  EventData


class DeepReportAgentBase(ABC):
    def __init__(self):
        self._event_notifier = EventNotifier()
        pass


    def event_notify(self, event_data: EventData) -> None:
        try:
            json_data = event_data.to_json()
            print(json_data)  # todo: remove
            self._event_notifier.send_message(event_data)
        except Exception as e:
            #todo: log notifica non inviata
            pass
