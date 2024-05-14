"""Message types for the Jedi Chat application"""

from datetime import datetime
import json
import html


class JediMessage:
    """Base class for all messages sent by the Jedi Chat application"""

    message_type: str
    group_name: str
    author: str
    created_at: str

    def to_json(self):
        """Converts the message to a JSON string"""
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_data: dict):
        """Converts a JSON object to a JediMessage"""
        return cls(**json_data)

    @property
    def display_event(self):
        """Returns a string representation of the event"""
        return f"{self.created_at}: {self.message_type} - {self.author}"


class DestinySwitchMessage(JediMessage):
    """A message that represents a change in the state of a destiny point"""

    point_id: int
    was_light: bool

    def __init__(
        self,
        point_id: int,
        was_light: bool,
        group_name: str,
        author: str,
        created_at: str = None,
        **_,
    ):
        """Creates a new DestinySwitchMessage object and fills base fields"""
        self.message_type = "DestinySwitchMessage"
        self.point_id = point_id
        self.was_light = was_light
        self.group_name = group_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

    @property
    def display_event(self):
        return f'{self.created_at}: {self.author} - Destiny Point({self.point_id}) {"switched to Dark" if self.was_light else "switched to Light"}'


class DestinyAddMessage(JediMessage):
    """A message that represents the addition of a new destiny point"""

    point_id: int
    is_light: bool

    def __init__(
        self,
        point_id: int,
        is_light: bool,
        group_name: str,
        author: str,
        created_at: str = None,
        **_,
    ):
        """Creates a new DestinyAddMessage object and fills base fields"""
        self.message_type = "DestinyAddMessage"
        self.point_id = point_id
        self.is_light = is_light
        self.group_name = group_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

    @property
    def display_event(self):
        return f'{self.created_at}: {self.author} - New Destiny Point({self.point_id}) {"is Light" if self.is_light else "is Dark"}'


class DestinyRemoveMessage(JediMessage):
    """A message that represents the removal of a destiny point"""

    point_id: int

    def __init__(
        self, point_id: int, group_name: str, author: str, created_at: str = None, **_
    ):
        """Creates a new DestinyRemoveMessage object and fills base fields"""
        self.message_type = "DestinyRemoveMessage"
        self.point_id = point_id
        self.group_name = group_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

    @property
    def display_event(self):
        return (
            f"{self.created_at}: {self.author} - Removed Destiny Point({self.point_id})"
        )


class CharacterCreateMessage(JediMessage):
    """A message that represents the creation of a new character"""

    char_name: str
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

    def __init__(
        self,
        group_name: str,
        author: str,
        char_name: str,
        wound_limit: int = 0,
        wound_current: int = 0,
        strain_limit: int = 0,
        strain_current: int = 0,
        defense_melee: int = 0,
        defense_ranged: int = 0,
        soak: int = 0,
        status_flags: str = "",
        image_url: str = "",
        initiative_triumph: int = 0,
        initiative_success: int = 0,
        initiative_advantage: int = 0,
        created_at: str = None,
        **_,
    ):
        """Creates a new CharacterCreateMessage object and fills base fields"""
        self.message_type = "CharacterCreateMessage"
        self.char_name = char_name
        self.wound_limit = wound_limit
        self.wound_current = wound_current
        self.strain_limit = strain_limit
        self.strain_current = strain_current
        self.defense_melee = defense_melee
        self.defense_ranged = defense_ranged
        self.soak = soak
        self.status_flags = status_flags
        self.image_url = image_url
        self.initiative_triumph = initiative_triumph
        self.initiative_success = initiative_success
        self.initiative_advantage = initiative_advantage
        self.group_name = group_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

    @property
    def display_event(self):
        return f"{self.created_at}: {self.author} - New Character({self.char_name}) created"


class CharacterUpdateMessage(JediMessage):
    """A message that represents the update of a character for one specific trait"""

    char_name: str
    trait_name: str
    trait_value: int | str

    def __init__(
        self,
        group_name: str,
        char_name: str,
        trait_name: str,
        trait_value: int | str,
        author: str,
        created_at: str = None,
        **_,
    ):
        """Creates a new CharacterUpdateMessage object and fills base fields"""
        self.message_type = "CharacterUpdateMessage"
        self.char_name = char_name
        self.trait_name = trait_name
        self.trait_value = trait_value
        self.group_name = group_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

    @property
    def display_event(self):
        return f"{self.created_at}: {self.author} - {self.char_name} updated {self.trait_name} to {self.trait_value}"


class CharacterDeleteMessage(JediMessage):
    """A message that represents the deletion of a character"""

    char_name: str

    def __init__(
        self, group_name: str, char_name: str, author: str, created_at: str = None, **_
    ):
        """Creates a new CharacterDeleteMessage object and fills base fields"""
        self.message_type = "CharacterDeleteMessage"
        self.char_name = char_name
        self.group_name = group_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

    @property
    def display_event(self):
        return f"{self.created_at}: {self.author} - Deleted Character({self.char_name})"


class RollReqestMessage(JediMessage):
    """A message that represents a request to roll dice"""

    dice_pool: str
    comment: str

    def __init__(
        self,
        group_name: str,
        char_name: str,
        author: str,
        dice_pool: str,
        comment: str,
        created_at: str = None,
        **_,
    ):
        """Creates a new RollReqestMessage object and fills base fields"""
        self.message_type = "RollReqestMessage"
        self.dice_pool = dice_pool
        self.comment = comment
        self.group_name = group_name
        self.char_name = char_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

symbol_lookup = {
    "empty": "",
    "despair": "y",
    "triumph": "x",
    "dark": "z",
    "light": "Z"
}

dice_class_lookup = {
    "proficiency": "pentagon bg-yellow-500 text-black",
    "ability": "rombus bg-green-500 text-black",
    "boost": "bg-sky-500 text-black",
    "setback": "bg-black text-white",
    "difficulty": "rombus bg-purple-600 text-black",
    "challenge": "pentagon bg-red-500 text-black",
    "force": "pentagon bg-white text-black"
}

dice_display_lookup = {
    "proficiency": "<div class='size-20 pentagon bg-yellow-500 text-black'></div>",
    "ability": "<div class='size-20 rombus bg-green-500 text-black'></div>",
    "boost": "<div class='size-20 bg-sky-500 text-black'></div>",
    "setback": "<div class='size-20 bg-black text-white'></div>",
    "difficulty": "<div class='size-20 rombus bg-purple-600 text-black'></div>",
    "challenge": "<div class='size-20 pentagon bg-red-500 text-black'></div>",
    "force": "<div class='size-20 pentagon bg-white text-black'></div>",
    "dark": "<div class='sw-symbol-font text-6xl text-white'>z</div>",
    "light": "<div class='sw-symbol-font text-6xl text-white'>Z</div>",
    "triumph": "<div class='sw-symbol-font text-6xl text-white'>x</div>",
    "success": "<div class='sw-symbol-font text-6xl text-white'>s</div>",
    "advantage": "<div class='sw-symbol-font text-6xl text-white'>a</div>",
    "despair": "<div class='sw-symbol-font text-6xl text-white'>y</div>",
    "failure": "<div class='sw-symbol-font text-6xl text-white'>f</div>",
    "threat": "<div class='sw-symbol-font text-6xl text-white'>t</div>",

}

class RollResultMessage(JediMessage):
    """A message that represents the result of a dice roll"""

    dice_pool: str
    result: str
    comment: str

    def __init__(
        self,
        group_name: str,
        char_name: str,
        author: str,
        dice_pool: str,
        result: str,
        comment: str,
        created_at: str = None,
        **_,
    ):
        """Creates a new RollResultMessage object and fills base fields"""
        self.message_type = "RollResultMessage"
        self.dice_pool = dice_pool
        self.result = result
        self.comment = comment
        self.group_name = group_name
        self.char_name = char_name
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%H:%M:%S")

    @property
    def display_event(self):
        result_dict:dict[str,list[str]] = json.loads(self.result)
        formatted_result = ""
        result_sums = {}
        for dice, results in result_dict.items():
            dice_classes = dice_class_lookup.get(dice, "font-white")
            for result in results:
                content = "".join(symbol_lookup.get(r, r.lower()[0]) for r in result.split("_"))
                for symbol in content:
                    result_sums[symbol] = result_sums.get(symbol, 0) + 1
                formatted_result += f'<span class="m-1 inline-block min-h-16 min-w-16 text-center content-center sw-symbol-font {dice_classes} {"text-lg" if "_" in result else ""}">{content}</span>'
        calculated_results = {
            'x': result_sums.get('x', 0),
            'y': result_sums.get('y', 0),
            's': result_sums.get('s', 0)-result_sums.get('f', 0),
            'f': result_sums.get('f', 0)-result_sums.get('s', 0),
            'a': result_sums.get('a', 0)-result_sums.get('t', 0),
            't': result_sums.get('t', 0)-result_sums.get('a', 0),
            'z': result_sums.get('z', 0)-result_sums.get('Z', 0),
            'Z': result_sums.get('Z', 0)-result_sums.get('z', 0),
        }
        if all(value <=0 for value in calculated_results.values()):
            message = "Alle Dice have cancelled each other out"
        else:
            message = 'Symbols Counted: '+ ', '.join(f'<span class=" sw-symbol-font text-white text-lg">{k}<span>: {v}' for k,v in calculated_results.items() if v>0)
        return f'{self.created_at}: {self.author} - {self.char_name} rolled <div class="flex flex-row flex-wrap">{formatted_result}</div> <br> {message} {"<br>"+html.escape(self.comment) if self.comment else ""}'
