"""
Message Bus for the Jedi Chat application.

where all messages are sent to and which registers message handlers for each message type
"""

from typing import Awaitable, Callable, Type

from app.connection_manager import ConnectionManager
from app.static.scripts.message_types import (
    DestinyAddMessage,
    DestinySwitchMessage,
    DestinyRemoveMessage,
    JediMessage,
    CharacterCreateMessage,
    CharacterDeleteMessage,
    CharacterUpdateMessage,
    RollReqestMessage,
    RollResultMessage,
)
MessageHandlerType = Callable[[Type[JediMessage]], Awaitable[Type[JediMessage]]]

class MessageBus:
    """Message Bus for the Jedi Chat application. where all messages are sent to and which registers message handlers for each message type"""

    handlers: dict[str, list[MessageHandlerType]]
    message_types: dict[str, Type[JediMessage]]
    message_history_handler: MessageHandlerType
    manager: ConnectionManager

    def __init__(self,manager:ConnectionManager):
        self.handlers = {}
        self.message_types = {
            "DestinyAddMessage": DestinyAddMessage,
            "DestinySwitchMessage": DestinySwitchMessage,
            "DestinyRemoveMessage": DestinyRemoveMessage,
            "CharacterCreateMessage": CharacterCreateMessage,
            "CharacterDeleteMessage": CharacterDeleteMessage,
            "CharacterUpdateMessage": CharacterUpdateMessage,
            "RollReqestMessage": RollReqestMessage,
            "RollResultMessage": RollResultMessage,

        }
        self.message_history_handler = None
        self.manager = manager

    def register_handler(self, message_type: str, handler: MessageHandlerType):
        """Registers a handler for a specific message type"""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)

    async def process_message(self, message_json: dict):
        """Processes a message by calling all registered handlers for its type"""
        if (
            message_json['message_type'] in self.handlers
            and message_json['message_type'] in self.message_types
            and self.handlers[message_json['message_type']]
        ):
            specialized_message = self.message_types[message_json['message_type']].from_json(
                message_json
            )
            print(f"Processing: {message_json} -> {type(specialized_message)}")
            for handler in self.handlers[message_json['message_type']]:
                specialized_message = await handler(specialized_message)
            if self.message_history_handler is not None:
                await self.message_history_handler(specialized_message)
            await self.manager.broadcast(specialized_message.group_name, specialized_message.to_json())
        else:
            print(f"No handler for message type {message_json['message_type']}")
