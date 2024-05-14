Open Todos:
* Technische Features
  * [x] Websocket zur Live Kommunikation
  * [x] Datenbank für Persistenz
  * ~~Message Channels (Destiny, Status, Würfel, Ereignis, Zeichnung)~~
  * [x] Message Broker
  * [x] Message History
  * [x] Message Author
  * Heartbeat
  * Auto Reconnect
  * Error Handling
  * rate limiting or throttling
  * [x] file separation
  * [x] styling framework (Tailwind)
    * color scheme (light dark starwarstheme)
    * animations for new elements
* Destiny Monitor
  * [x] Destiny Punkte anzeigen (persistent)
  * [x] Destiny Punkte schalten
  * [x] Destiny Punkte hinzufügen
  * [x] Destiny Punkte entfernen
* [x] Status - Tabelle Charaktere HP Stress Rüstung Absorb (Bild) ~~(Credits)~~
  * UI UX verbessern
  * [x] Editierbar
  * Sortierbar (Ini)
  * NSC Slots
* Würfel App
  * [x] Würfel Pool einstellen
    * Würfel vergeben
  * [x] Würfel Ergebnis
    * letztes Würfelergebnis je Charakter
  * Spezialwürfe
  * Ergebnisshop (Vorteile, Nachteile, Triumph, Verzweiflung)
  * Kampfmodus
    * Initiative
    * Runden
    * Doppelte Aktion (Erschöpfung)
* [x] Ereignis - Historie
  * Ereignis entfernen
* Zeichnungen
  * Freihand
  * Geometrische Formen
  * Text
  * Farben
  * Ebenen (Oberste Ebene = > Tokens)
  * Bilder

* [x] Live Feedback, refresh der Infos
* [x] Gruppenräume


# Layers
Adding a new component to the page probably touching the following layers:
* `models.py` -> if it is **stateful**, the state model needs to be defined here
* `/static/scripts/message_types.py` -> if it has a specific **message type** it needs to be defined here
* `db_controller.py` -> define a method for getting the **state** of a group for the new component. Also define methods for updating the **state** of the new component, which will be called by the message handlers so the param needs to be the same as the message type
* `main.py` -> if it is **stateful**, the state needs to be loaded here
* `message_bus.py` -> if it has a specific **message type** it needs to be registered here
* `/templates/components/{BLAB}.html` -> the new **BLAB** component needs to be defined here
* `/static/scripts/{BLAB}_message_handler.py` -> if it uses some **messages**, a new handler should be created, implementing the abstract `MessageHandler` interface
* `/static/scripts/pywebsocket.py` -> the new **BLABMessageHandler** needs to be registered here
* `/templates/mainpage.html` -> the new **BLAB** component needs to be included here, also include the scripts in the py-config files list

## Example: Adding CharacterState Component

1. `models.py`:

Define the state model for the new component. We will need a list of characters with their current state.
```python
class CharacterState(SQLModel, table=True):
    """Each Group can has multiple Characters, this class represents the state of a single Character for a specific Group."""

    group_name: str = Field(primary_key=True)
    char_name: str = Field(primary_key=True)
    wound_limit: int
    wound_current: int
    strain_limit: int
    strain_current: int
    defense_melee: int
    defense_ranged: int
    soak: int
    status_flags: str
    image_url: str
    initiative_triumph: int
    initiative_success: int
    initiative_advantage: int

    @property
    def stati(self):
        '''Returns a list of the status flags'''
        return self.status_flags.split(',') if self.status_flags else []
```

2. `message_types.py`:

Define the message type for the new component. We will need a message to update the state of a character.
```python
class CharacterCreateMessage(JediMessage):
    """A message that represents the creation of a new character"""

    char_name: str
    ... # shortened for brevity

    def __init__(
        self,
        group_name: str,
        author: str,
        char_name: str,
        ... # shortened for brevity
        **_,
    ):
        """Creates a new CharacterCreateMessage object and fills base fields"""
        self.message_type = "CharacterCreateMessage"
        self.char_name = char_name
        self.group_name = group_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")
        ... # shortened for brevity

    @property
    def display_event(self):
        return f"{self.created_at}: {self.author} - New Character({self.char_name}) created"

class CharacterUpdateMessage(JediMessage):
    """A message that represents the update of a character for one specific trait"""

    ... # shortened for brevity

class CharacterDeleteMessage(JediMessage):
    """A message that represents the deletion of a character"""

    ... # shortened for brevity
```

3. `db_controller.py`:

We need a get all and a method for each of the three message types. Validation is omitted for brevity.
```python
def get_character_states(group_name: str, session: Session):
    """Gets the current state of a character."""
    return session.exec(
        select(CharacterState).where(CharacterState.group_name == group_name)
    ).all()

def create_character_state(message: CharacterCreateMessage):
    """Creates a new character state."""
    with Session(engine) as session:
        new_state = CharacterState(**message.to_dict())
        session.add(new_state)
        session.commit()
    return message

def update_character_state(message: CharacterUpdateMessage):
    """Updates the state of a character."""
    with Session(engine) as session:
        character_state = session.exec(
            select(CharacterState).where(
                CharacterState.group_name == message.group_name,
                CharacterState.char_name == message.char_name,
            )
        ).first()
        setattr(character_state, message.trait_name, message.trait_value)
        session.commit()
    return message

def delete_character_state(message: CharacterDeleteMessage):
    """Deletes a character state."""
    with Session(engine) as session:
        character_state = session.exec(
            select(CharacterState).where(
                CharacterState.group_name == message.group_name,
                CharacterState.char_name == message.char_name,
            )
        ).first()
        session.delete(character_state)
        session.commit()
    return message
```

4. `main.py`:
In the only relevant Route we call the get_character_states method and pass the result to the template.
```python
@app.get("/main/{group_name}/")
async def get_group_state(
    request: Request,
    group_name: str,
    char_name: str,
    session: Session = Depends(get_session),
):
    # get other states
    ...

    # get character states
    character_states = get_character_states(group_name, session)

    return templates.TemplateResponse(
        "testpage.html",
        {
            "request": request,
            ... # shortened for brevity
            "character_states": character_states,
        },
    )
```

5. `message_bus.py`:
Here we just need to register the new message types in the init method.
```python
def __init__(self,manager:ConnectionManager):
    self.handlers = {}
    self.message_type = {
        ... # other message types
        "CharacterCreateMessage": CharacterCreateMessage,
        "CharacterDeleteMessage": CharacterDeleteMessage,
        "CharacterUpdateMessage": CharacterUpdateMessage,
    }
```

6. `/templates/components/character_state.html`:
Define the new component in the template.
```html
<h2 style="margin: 0px">Characters:</h2>
<table>
    <thead>
        <tr>
            <th>Character</th>
            <th>Wounds/Limit</th>
            <th>Strain/Limit</th>
            <th>Defense Melee/Ranged</th>
            <th>Soak</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="character-table-body">
        {% for character in character_states %}
        <tr id="character-row-{{character.char_name}}">
            <td>{{ character.char_name }}</td>
            <td>{{ character.wound_current }}/{{ character.wound_limit }}</td>
            <td>{{ character.strain_current }}/{{ character.strain_limit }}</td>
            <td>{{ character.defense_melee }}/{{ character.defense_ranged }}</td>
            <td>{{ character.soak }}</td>
            <td>{{ character.status }}</td>
            <td>
                <button class="bg-sky-700 hover:bg-sky-300 size-8 hexagon" id="action-{{character.char_name}}-increase-wound">+ HP</button>
                <button class="bg-sky-700 hover:bg-sky-300 size-8 hexagon" id="action-{{character.char_name}}-increase-strain">+ S</button>
                <button class="bg-red-800 hover:bg-red-300 size-8 hexagon" id="action-{{character.char_name}}-decrease-wound">- HP</button>
                <button class="bg-red-800 hover:bg-red-300 size-8 hexagon" id="action-{{character.char_name}}-decrease-strain">- S</button>
                <button class="bg-sky-700 hover:bg-sky-300 size-8 hexagon" id="action-{{character.char_name}}-edit"> edit </button>
                <button class="bg-red-800 hover:bg-red-300 size-8 hexagon" id="action-{{character.char_name}}-delete"> delete </button>
        </tr>
        {% endfor %}
    </tbody>
</table>
<button id="add-character-button" class="bg-sky-700 hover:bg-sky-300 size-8 hexagon">NEW</button>
```

7. `/static/scripts/character_state_message_handler.py`:
Define the message handler for the new component. And add_event_listener for the new actions.
```python
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
            action_cell.create("button", id=f"action-{message.char_name}-increase-wound", html="+ HP", classes="bg-red-700 hover:bg-red-300 size-8 hexagon")
            action_cell.create("button", id=f"action-{message.char_name}-increase-strain", html="+ S", classes="bg-red-700 hover:bg-red-300 size-8 hexagon")
            action_cell.create("button", id=f"action-{message.char_name}-decrease-wound", html="- HP", classes="bg-sky-700 hover:bg-sky-300 size-8 hexagon")
            action_cell.create("button", id=f"action-{message.char_name}-decrease-strain", html="- S", classes="bg-sky-700 hover:bg-sky-300 size-8 hexagon")
            action_cell.create("button", id=f"action-{message.char_name}-edit", html="Edit", classes="bg-yellow-700 hover:bg-yellow-300 size-8 hexagon")
            action_cell.create("button", id=f"action-{message.char_name}-delete", html="Delete", classes="bg-red-700 hover:bg-red-300 size-8 hexagon")
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
            # TODO update the table
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
        current_wound = int(pydom[f"#character-row-{char_name} td:nth-child(2)"][0].text.split(" / ")[0])
        self.ws.send(self.make_character_update_message(char_name,"wound_current",current_wound+1))

    def decrease_wound(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Decreasing Wound: {char_name}")
        current_wound = int(pydom[f"#character-row-{char_name} td:nth-child(2)"][0].text.split(" / ")[0])
        self.ws.send(self.make_character_update_message(char_name,"wound_current",current_wound-1))

    def increase_strain(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Increasing Strain: {char_name}")
        current_strain = int(pydom[f"#character-row-{char_name} td:nth-child(3)"][0].text.split(" / ")[0])
        self.ws.send(self.make_character_update_message(char_name,"strain_current",current_strain+1))

    def decrease_strain(self, event):
        char_name = event.target.id.split("-")[1]
        print(f"Decreasing Strain: {char_name}")
        current_strain = int(pydom[f"#character-row-{char_name} td:nth-child(3)"][0].text.split(" / ")[0])
        self.ws.send(self.make_character_update_message(char_name,"strain_current",current_strain-1))
```

8. `/static/scripts/pywebsocket.py`:
Register the new message handler in the init method.
```python
...
url_params = {
    param.split("=")[0]: param.split("=", 1)[1]
    for param in window.location.search.lstrip("?").split("&")
}
client_name = url_params["char_name"]
group_name = window.location.pathname.split("/")[2]
ws = WebSocket.new(f"ws://{window.location.host}/ws/{group_name}/{client_name}")


message_handlers = [
    ... # other message handlers
    CharacterStateMessageHandler(group_name, client_name, ws),
]
...
```

9. `/templates/mainpage.html`:
Include the new component in the main page. Also include the scripts in the py-config files list.

```html
...
   {% include 'components/character_state.html' %}
...
<py-config>
      [[fetch]]
      from="../../static/scripts/"
      files = ["message_types.py","destiny_message_handler.py","message_handler_base.py","character_state_message_handler.py"]
    </py-config>
```

DONE! Now manually test the shit out of it
.

.

.

.



# *Note from past ME: (Tldr -> sorry)*

*I really should have set up automatic testing and not skipped it because of testing pyscript, websockets, concurrency and html browser clicking is hard. Now it is up to **YOU**. Maybe **selenium** can help with the clicky part. And maybe you build a client directly connecting to the websocket without the browser.*

