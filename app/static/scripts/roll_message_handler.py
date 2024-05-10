import json

from js import WebSocket, document,window
from message_handler_base import MessageHandler, add_on_click_listeners
from message_types import RollReqestMessage
from pyweb import pydom

@add_on_click_listeners
class RollMessageHandler(MessageHandler):
    ws: WebSocket
    group_name: str
    client_name: str
    dice_pool: dict[str,int]

    def __init__(self, group_name: str, client_name: str, ws: WebSocket):
        super().__init__(group_name, client_name, ws)
        self.dice_pool = {}

    def process_message(self, raw_message: str):
        print(f"Processing: {raw_message}")
        # if "RollReqestMessage" in raw_message:
        #     return self.receive_roll_request_message(raw_message)
        # if "RollResultMessage" in raw_message:
        #     return self.receive_roll_result_message(raw_message)
        print(f"Unknown message: {raw_message}")


    def on_click_dice_proficiency_up(self, *_, **__):
        self.dice_pool["proficiency"] = self.dice_pool.get("proficiency", 0) + 1
        pydom["#dice-proficiency-count"][0].html = str(self.dice_pool.get("proficiency",0))

    def on_click_dice_ability_up(self, *_, **__):
        self.dice_pool["ability"] = self.dice_pool.get("ability", 0) + 1
        pydom["#dice-ability-count"][0].html = str(self.dice_pool.get("ability",0))

    def on_click_dice_boost_up(self, *_, **__):
        self.dice_pool["boost"] = self.dice_pool.get("boost", 0) + 1
        pydom["#dice-boost-count"][0].html = str(self.dice_pool.get("boost",0))

    def on_click_dice_setback_up(self, *_, **__):
        self.dice_pool["setback"] = self.dice_pool.get("setback", 0) + 1
        pydom["#dice-setback-count"][0].html = str(self.dice_pool.get("setback",0))

    def on_click_dice_difficulty_up(self, *_, **__):
        self.dice_pool["difficulty"] = self.dice_pool.get("difficulty", 0) + 1
        pydom["#dice-difficulty-count"][0].html = str(self.dice_pool.get("difficulty",0))

    def on_click_dice_challenge_up(self, *_, **__):
        self.dice_pool["challenge"] = self.dice_pool.get("challenge", 0) + 1
        pydom["#dice-challenge-count"][0].html = str(self.dice_pool.get("challenge",0))

    def on_click_dice_force_up(self, *_, **__):
        self.dice_pool["force"] = self.dice_pool.get("force", 0) + 1
        pydom["#dice-force-count"][0].html = str(self.dice_pool.get("force",0))

    def on_click_dice_proficiency_down(self, *_, **__):
        self.dice_pool["proficiency"] = max(0,self.dice_pool.get("proficiency", 0) - 1)
        pydom["#dice-proficiency-count"][0].html = str(self.dice_pool.get("proficiency",0))

    def on_click_dice_ability_down(self, *_, **__):
        self.dice_pool["ability"] = max(0,self.dice_pool.get("ability", 0) - 1)
        pydom["#dice-ability-count"][0].html = str(self.dice_pool.get("ability",0))

    def on_click_dice_boost_down(self, *_, **__):
        self.dice_pool["boost"] = max(0,self.dice_pool.get("boost", 0) - 1)
        pydom["#dice-boost-count"][0].html = str(self.dice_pool.get("boost",0))

    def on_click_dice_setback_down(self, *_, **__):
        self.dice_pool["setback"] = max(0,self.dice_pool.get("setback", 0) - 1)
        pydom["#dice-setback-count"][0].html = str(self.dice_pool.get("setback",0))

    def on_click_dice_difficulty_down(self, *_, **__):
        self.dice_pool["difficulty"] = max(0,self.dice_pool.get("difficulty", 0) - 1)
        pydom["#dice-difficulty-count"][0].html = str(self.dice_pool.get("difficulty",0))

    def on_click_dice_challenge_down(self, *_, **__):
        self.dice_pool["challenge"] = max(0,self.dice_pool.get("challenge", 0) - 1)
        pydom["#dice-challenge-count"][0].html = str(self.dice_pool.get("challenge",0))

    def on_click_dice_force_down(self, *_, **__):
        self.dice_pool["force"] = max(0,self.dice_pool.get("force", 0) - 1)
        pydom["#dice-force-count"][0].html = str(self.dice_pool.get("force",0))

    def on_click_roll_dice_button(self, *_, **__):
        payload = json.dumps(self.dice_pool)
        keep_pool = document.getElementById('dice-keep-numbers').checked
        if not keep_pool:
            self.dice_pool = {}
            pydom["#dice-proficiency-count"][0].html = "0"
            pydom["#dice-ability-count"][0].html = "0"
            pydom["#dice-boost-count"][0].html = "0"
            pydom["#dice-setback-count"][0].html = "0"
            pydom["#dice-difficulty-count"][0].html = "0"
            pydom["#dice-challenge-count"][0].html = "0"
            pydom["#dice-force-count"][0].html = "0"

        self.ws.send(str(RollReqestMessage(
            self.group_name,
            self.client_name,
            self.client_name,
            payload,
            pydom["#dice-comment"][0].value,
        ).to_json()))
