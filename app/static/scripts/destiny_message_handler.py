import json

from js import WebSocket, document
from message_handler_base import MessageHandler
from message_types import DestinyAddMessage, DestinyRemoveMessage, DestinySwitchMessage
from pyodide.ffi.wrappers import add_event_listener
from pyweb import pydom


class DestinyMessageHandler(MessageHandler):
    ws: WebSocket
    group_name: str
    client_name: str

    def __init__(self, group_name: str, client_name: str, ws: WebSocket):
        super().__init__(group_name, client_name, ws)
        self.attach_listeners()

    def process_message(self, raw_message: str):
        print(f"Processing: {raw_message}")
        if "DestinySwitchMessage" in raw_message:
            return self.receive_destiny_switch_message(raw_message)
        if "DestinyAddMessage" in raw_message:
            return self.receive_destiny_add_message(raw_message)
        if "DestinyRemoveMessage" in raw_message:
            return self.receive_destiny_remove_message(raw_message)
        print(f"Unknown message: {raw_message}")

    def attach_listeners(self):
        monitor = pydom["#destiny-monitor"][0]
        for child_point in monitor.children:
            print("attaching listener to", child_point.id.split("-")[-1])
            add_event_listener(
                document.getElementById(child_point.id),
                "click",
                self.switch_destiny,
            )
        add_event_listener(
            document.getElementById("add-destiny-button"),
            "click",
            lambda event: self.ws.send(self.make_destiny_add_message()),
        )
        add_event_listener(
            document.getElementById("remove-destiny-button"),
            "click",
            lambda event: self.ws.send(self.make_destiny_remove_message(1)),
        )

    def make_destiny_switch_message(self, destiny_state_id: int):
        return DestinySwitchMessage(
            destiny_state_id,
            pydom[f"#destiny-{destiny_state_id}"][0].style["background-color"]
            == "yellow",
            self.group_name,
            self.client_name,
        ).to_json()

    def switch_destiny(self, event):
        print(f"Switching: {event.target.id}")
        self.ws.send(self.make_destiny_switch_message(event.target.id.split("-")[-1]))

    def receive_destiny_switch_message(self, raw_message: str):
        try:
            message = DestinySwitchMessage(**json.loads(raw_message))
        except json.JSONDecodeError:
            print(f"Invalid JSON: {raw_message}")
            return None
        print(f"Received DestinySwitchMessage: {message.point_id}")
        point_display = pydom[f"#destiny-{message.point_id}"][0]
        if message.was_light:
            point_display.style["background-color"] = "black"
        else:
            point_display.style["background-color"] = "yellow"
        return message

    def make_destiny_add_message(
        self, destiny_state_id: int = -1, is_light: bool = True
    ):
        result = DestinyAddMessage(
            destiny_state_id, is_light, self.group_name, self.client_name
        ).to_json()
        print(f"Sending: {result}")
        return str(result)

    def receive_destiny_add_message(self, raw_message: str):
        try:
            message = DestinyAddMessage(**json.loads(raw_message))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {raw_message}\n{e}")
            return None
        new_point = pydom["#destiny-monitor"][0].create("li")
        new_point.id = f"destiny-{message.point_id}"
        new_point.style["background-color"] = "yellow" if message.is_light else "black"
        new_point.style["width"] = "64px"
        new_point.style["height"] = "64px"
        new_point.style["border-radius"] = "50%"
        new_point.style["display"] = "inline-block"
        new_point.style["margin"] = "5px"
        new_point.style["cursor"] = "pointer"
        add_event_listener(
            document.getElementById(f"destiny-{message.point_id}"),
            "click",
            self.switch_destiny,
        )
        return message

    def receive_destiny_remove_message(self, raw_message: str):
        try:
            message = DestinyRemoveMessage(**json.loads(raw_message))
        except json.JSONDecodeError:
            print(f"Invalid JSON: {raw_message}")
            return None
        print(f"Received DestinyRemoveMessage: {message.point_id}")
        pydom[f"#destiny-{message.point_id}"][0].remove()
        return message

    def make_destiny_remove_message(self, destiny_state_id: int):
        return DestinyRemoveMessage(
            destiny_state_id, self.group_name, self.client_name
        ).to_json()
