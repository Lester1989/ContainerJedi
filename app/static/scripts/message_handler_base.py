from abc import ABC, abstractmethod

from js import WebSocket


class MessageHandler(ABC):
    ws: WebSocket
    group_name: str
    client_name: str

    def __init__(self, group_name: str, client_name: str, ws: WebSocket):
        self.client_name = client_name
        self.group_name = group_name
        self.ws = ws

    @abstractmethod
    def process_message(self, raw_message: str):
        pass
