import json

from js import WebSocket, document, window
from message_handler_base import MessageHandler
from message_types import CharacterCreateMessage, CharacterDeleteMessage, CharacterUpdateMessage
from pyodide.ffi.wrappers import add_event_listener
from pyweb import pydom

class CharacterStateMessageHandler(MessageHandler):
    ws: WebSocket
    group_name: str
    client_name: str

    def __init__(self, group_name: str, client_name: str, ws: WebSocket):
        super().__init__(group_name, client_name, ws)
        self.attach_listeners()

    def process_message(self, raw_message: str):
        print(f"Processing: {raw_message}")
        if "CharacterCreateMessage" in raw_message:
            return self.receive_character_create_message(raw_message)
        if "CharacterUpdateMessage" in raw_message:
            return self.receive_character_update_message(raw_message)
        if "CharacterDeleteMessage" in raw_message:
            return self.receive_character_delete_message(raw_message)
        print(f"Unknown message: {raw_message}")

    def attach_listeners(self):
        monitor = pydom["#character-table-body"][0]
        for child_point in monitor.children:
            char_name = child_point.id.split("-")[-1]
            print("attaching listeners to", char_name)

            add_event_listener(
                document.getElementById(f"action-{char_name}-increase-wound"),
                "click",
                self.increase_wound,
            )
            add_event_listener(
                document.getElementById(f"action-{char_name}-decrease-wound"),
                "click",
                self.decrease_wound,
            )
            add_event_listener(
                document.getElementById(f"action-{char_name}-increase-strain"),
                "click",
                self.increase_strain,
            )
            add_event_listener(
                document.getElementById(f"action-{char_name}-decrease-strain"),
                "click",
                self.decrease_strain,
            )
            add_event_listener(
                document.getElementById(f"action-{char_name}-edit"),
                "click",
                self.edit_character,
            )
            add_event_listener(
                document.getElementById(f"action-{char_name}-delete"),
                "click",
                self.delete_character,
            )
        add_event_listener(
            document.getElementById("add-character-button"),
            "click",
            self.create_character,
        )

    def create_character(self, event):
        char_name = window.prompt("Character Name","")
        if char_name:
            self.ws.send(self.make_character_create_message(char_name))

    def make_character_create_message(self,char_name:str):
        return CharacterCreateMessage(
            self.group_name,
            self.client_name,
            char_name=char_name,
        ).to_json()

    def receive_character_create_message(self, raw_message: str):
        try:
            message = CharacterCreateMessage(**json.loads(raw_message))
            new_row = pydom["#character-table-body"][0].create("tr")
            new_row.id = f"character-row-{message.char_name}"
            new_row.create("td", html=message.char_name)
            new_row.create("td", html=f"{message.wound_current} / {message.wound_limit}")
            new_row.create("td", html=f"{message.strain_current} / {message.strain_limit}")
            new_row.create("td", html=f"{message.defense_melee} / {message.defense_ranged}")
            new_row.create("td", html=f"{message.soak}")
            new_row.create("td", html=f"{message.status_flags}")
            action_cell = new_row.create("td")
            button = action_cell.create("button", html="+ HP", classes=["bg-red-700","hover:bg-red-300", "size-8", "hexagon"])
            button.id=f"action-{message.char_name}-increase-wound"
            button = action_cell.create("button",  html="+ S", classes=["bg-red-700","hover:bg-red-300", "size-8", "hexagon"])
            button.id=f"action-{message.char_name}-increase-strain"
            button = action_cell.create("button", html="- HP", classes=["bg-sky-700","hover:bg-sky-300", "size-8", "hexagon"])
            button.id=f"action-{message.char_name}-decrease-wound"
            button = action_cell.create("button",  html="- S", classes=["bg-sky-700","hover:bg-sky-300", "size-8", "hexagon"])
            button.id=f"action-{message.char_name}-decrease-strain"
            button = action_cell.create("button", html="Edit", classes=["bg-yellow-700","hover:bg-yellow-300", "size-8", "hexagon"])
            button.id=f"action-{message.char_name}-edit"
            button = action_cell.create("button", html="Delete", classes=["bg-red-700","hover:bg-red-300", "size-8", "hexagon"])
            button.id=f"action-{message.char_name}-delete"
            add_event_listener(
                document.getElementById(f"action-{message.char_name}-increase-wound"),
                "click",
                self.increase_wound,
            )
            add_event_listener(
                document.getElementById(f"action-{message.char_name}-decrease-wound"),
                "click",
                self.decrease_wound,
            )
            add_event_listener(
                document.getElementById(f"action-{message.char_name}-increase-strain"),
                "click",
                self.increase_strain,
            )
            add_event_listener(
                document.getElementById(f"action-{message.char_name}-decrease-strain"),
                "click",
                self.decrease_strain,
            )
            add_event_listener(
                document.getElementById(f"action-{message.char_name}-edit"),
                "click",
                self.edit_character,
            )
            add_event_listener(
                document.getElementById(f"action-{message.char_name}-delete"),
                "click",
                self.delete_character,
            )
            return message
        except Exception as e:
            print(f"Error processing message: {raw_message}")
            print(e)

    def edit_character(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Editing: {char_name}")
        trait = window.prompt("Trait Name","")
        if trait:
            value = window.prompt("Trait Value","")
            if value:
                self.ws.send(self.make_character_update_message(char_name,trait,value))

    def make_character_update_message(self, char_name: str,trait:str,value:str|int):
        return CharacterUpdateMessage(
            self.group_name,
            char_name,
            author=self.client_name,
            trait_name=trait,
            trait_value=value,
        ).to_json()

    def receive_character_update_message(self, raw_message: str):
        try:
            message = CharacterUpdateMessage(**json.loads(raw_message))
            if message.trait_name == "wound_current":
                old_value:str = pydom[f"#character-row-{message.char_name} td:nth-child(2)"][0].text
                new_value:str = f"{message.trait_value} / {old_value.split('/')[1]}"
                pydom[f"#character-row-{message.char_name} td:nth-child(2)"][0].text = new_value
            elif message.trait_name == "strain_current":
                old_value:str = pydom[f"#character-row-{message.char_name} td:nth-child(3)"][0].text
                new_value:str = f"{message.trait_value} / {old_value.split('/')[1]}"
                pydom[f"#character-row-{message.char_name} td:nth-child(3)"][0].text = new_value
            elif message.trait_name == "defense_melee":
                pydom[f"#character-row-{message.char_name} td:nth-child(4)"][0].text = f"{message.trait_value} / {pydom[f'#character-row-{message.char_name} td:nth-child(4)'][0].text.split('/')[1]}"
            elif message.trait_name == "defense_ranged":
                pydom[f"#character-row-{message.char_name} td:nth-child(4)"][0].text = f"{pydom[f'#character-row-{message.char_name} td:nth-child(4)'][0].text.split('/')[0]} / {message.trait_value}"
            elif message.trait_name == "soak":
                pydom[f"#character-row-{message.char_name} td:nth-child(5)"][0].text = f"{message.trait_value}"
            elif message.trait_name == "status_flags":
                pydom[f"#character-row-{message.char_name} td:nth-child(6)"][0].text = f"{message.trait_value}"
            return message
        except Exception as e:
            print(f"Error processing message: {raw_message}")
            print(e)

    def delete_character(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Deleting: {char_name}")
        self.ws.send(self.make_character_delete_message(char_name))

    def make_character_delete_message(self, char_name: str):
        return CharacterDeleteMessage(
            self.group_name,
            char_name,
            self.client_name,
        ).to_json()

    def receive_character_delete_message(self, raw_message: str):
        try:
            message = CharacterDeleteMessage(**json.loads(raw_message))
            pydom[f"#character-row-{message.char_name}"][0].remove()
            return message
        except Exception as e:
            print(f"Error processing message: {raw_message}")
            print(e)

    def increase_wound(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Increasing Wound: {char_name}")
        current_wound = int(pydom[f"#character-row-{char_name} td:nth-child(2)"][0].text.split("/")[0])
        self.ws.send(self.make_character_update_message(char_name,"wound_current",current_wound+1))

    def decrease_wound(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Decreasing Wound: {char_name}")
        current_wound = int(pydom[f"#character-row-{char_name} td:nth-child(2)"][0].text.split("/")[0])
        self.ws.send(self.make_character_update_message(char_name,"wound_current",current_wound-1))

    def increase_strain(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Increasing Strain: {char_name}")
        current_strain = int(pydom[f"#character-row-{char_name} td:nth-child(3)"][0].text.split("/")[0])
        self.ws.send(self.make_character_update_message(char_name,"strain_current",current_strain+1))

    def decrease_strain(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Decreasing Strain: {char_name}")
        current_strain = int(pydom[f"#character-row-{char_name} td:nth-child(3)"][0].text.split("/")[0])
        self.ws.send(self.make_character_update_message(char_name,"strain_current",current_strain-1))

