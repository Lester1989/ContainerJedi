"""Message types for the Jedi Chat application"""

from datetime import datetime
import json


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
