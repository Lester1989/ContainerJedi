"""This module contains the dependencies that will be used in the FastAPI application."""

from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.connection_manager import ConnectionManager
from app.db_controller import (
    store_history_event,
    add_destiny_state,
    delete_destiny_state,
    update_destiny_state,
    update_character_state,
    delete_character_state,
    create_character_state,
)
from app.message_bus import MessageBus
from app.models import engine


def get_session():
    """Yields a new session to the database"""
    with Session(engine) as session:
        yield session


templates = Jinja2Templates(directory="app/templates")


manager = ConnectionManager()

message_bus = MessageBus(manager)
message_bus.message_history_handler = store_history_event
message_bus.register_handler("DestinyAddMessage", add_destiny_state)
message_bus.register_handler("DestinySwitchMessage", update_destiny_state)
message_bus.register_handler("DestinyRemoveMessage", delete_destiny_state)
message_bus.register_handler("CharacterCreateMessage", create_character_state)
message_bus.register_handler("CharacterDeleteMessage", delete_character_state)
message_bus.register_handler("CharacterUpdateMessage", update_character_state)
