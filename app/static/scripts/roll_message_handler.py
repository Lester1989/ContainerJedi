import json

from js import WebSocket, document,window
from message_handler_base import MessageHandler, add_on_click_listeners
from message_types import RollReqestMessage,RollResultMessage,dice_display_lookup
from pyweb import pydom
from pyodide.ffi.wrappers import add_event_listener

@add_on_click_listeners
class RollMessageHandler(MessageHandler):
    ws: WebSocket
    group_name: str
    client_name: str
    dice_pool: dict[str,int]

    def __init__(self, group_name: str, client_name: str, ws: WebSocket):
        super().__init__(group_name, client_name, ws)
        self.dice_pool = {}
        for dice_name in dice_display_lookup:
            add_event_listener(
                document.getElementById(f"dice-{dice_name}-up"),
                "click",
                self.handle_dice_count_button,
            )
            add_event_listener(
                document.getElementById(f"dice-{dice_name}-down"),
                "click",
                self.handle_dice_count_button,
            )

    def process_message(self, raw_message: str):
        print(f"Processing: {raw_message}")
        # if "RollReqestMessage" in raw_message:
        #     return self.receive_roll_request_message(raw_message)
        if "RollResultMessage" in raw_message:
            return self.receive_roll_result_message(raw_message)
        print(f"Unknown message: {raw_message}")

    def receive_roll_result_message(self, raw_message: str):
        try:
            message = RollResultMessage(**json.loads(raw_message))
        except json.JSONDecodeError:
            print(f"Invalid JSON: {raw_message}")
            return None
        return message
    
    def handle_dice_count_button(self, event):
        dice_name = event.target.id.split("-")[-2]
        count_up = 1 if event.target.id.split("-")[-1] == "up" else -1
        self.dice_pool[dice_name] = max(0,self.dice_pool.get(dice_name, 0) + count_up)
        pydom[f"#dice-{dice_name}-count"][0].html = str(self.dice_pool.get(dice_name,0))

    
    def on_click_roll_dice_button(self, *_, **__):
        payload = json.dumps(self.dice_pool)
        keep_pool = document.getElementById('dice-keep-numbers').checked
        if not keep_pool:
            self.dice_pool = {}
            
            for dice_name in dice_display_lookup:
                pydom[f"#dice-{dice_name}-count"][0].html = "0"

        self.ws.send(str(RollReqestMessage(
            self.group_name,
            self.client_name,
            self.client_name,
            payload,
            pydom["#dice-comment"][0].value,
        ).to_json()))
