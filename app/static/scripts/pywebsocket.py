import json

from js import WebSocket, document
from destiny_message_handler import DestinyMessageHandler
from character_state_message_handler import CharacterStateMessageHandler
from roll_message_handler import RollMessageHandler
from pyscript import window
from pyweb import pydom

window.console.log("location", window.location)
url_params = {
    param.split("=")[0]: param.split("=", 1)[1]
    for param in window.location.search.lstrip("?").split("&")
}
client_name = url_params["char_name"]
group_name = window.location.pathname.split("/")[2]
ws = WebSocket.new(f"ws://{window.location.host}/ws/{group_name}/{client_name}")

message_handlers = [
    DestinyMessageHandler(group_name, client_name, ws),
    CharacterStateMessageHandler(group_name, client_name, ws),
    RollMessageHandler(group_name, client_name, ws),
]

def my_on_error(event):
    window.console.error(event)


def my_on_open(event):
    print("Opened")
    ws.send("Hello for the first time!")
    print(event)
    pydom["#socket-status-indicator"][0].style["background-color"] = "green"


def my_on_message(event):
    message = None
    window.console.log("received:", event.data)
    for handler in message_handlers:
        message = handler.process_message(event.data)
        if message:
            new_log_entry = pydom["#messages"][0].create("li", html=message.display_event)
            print(new_log_entry)
            # TODO: style history
            break
    else:
        print(f"Unknown message: {event.data}")


def my_on_close(event):
    print(event)
    window.console.log("Closed")
    pydom["#socket-status-indicator"][0].style["background-color"] = "rgb(239 68 68 / 0.7)"


ws.onclose = my_on_close
ws.onopen = my_on_open
ws.onmessage = my_on_message

pydom["#ws-id"][0].html = client_name
pydom["#loading-blocker"][0].style["display"] = "none"
