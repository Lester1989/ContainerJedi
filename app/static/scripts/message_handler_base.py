from abc import ABC, abstractmethod
import functools

from js import WebSocket, document
from pyodide.ffi.wrappers import add_event_listener


def add_on_click_listeners(cls):
    org_init = cls.__init__

    @functools.wraps(org_init)
    def new_init(self, *args, **kwargs):
        org_init(self, *args, **kwargs)
        for name, method in cls.__dict__.items():
            if callable(method) and name.startswith("on_click"):
                add_event_listener(
                    document.getElementById(name.replace("on_click_", "").replace("_", "-")),
                    "click",
                    functools.partial(method, self),
                )

    cls.__init__ = new_init

    return cls


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
