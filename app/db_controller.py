"""This module contains the functions that interact with the database."""

from datetime import datetime
from typing import Type

from sqlmodel import Session, select

from app.models import DestinyState, HistoryEvent, engine, CharacterState
from app.static.scripts.message_types import (
    DestinyAddMessage,
    DestinySwitchMessage,
    DestinyRemoveMessage,
    JediMessage,
    CharacterCreateMessage,
    CharacterDeleteMessage,
    CharacterUpdateMessage,
)

#+ DESTINY
def get_destiny_state(group_name: str, session: Session):
    """Gets the current state of the destiny points for a group."""
    return session.exec(
        select(DestinyState).where(DestinyState.group_name == group_name)
    ).all()


async def add_destiny_state(message: DestinyAddMessage):
    """Adds a new destiny state to the database."""
    with Session(engine) as session:
        new_state_id = (
            len(
                session.exec(
                    select(DestinyState).where(
                        DestinyState.group_name == message.group_name
                    )
                ).all()
            )
            + 1
        )
        new_state = DestinyState(
            group_name=message.group_name, is_light=message.is_light, id=new_state_id
        )
        session.add(new_state)
        session.commit()
        message.point_id = new_state_id
    return message


async def update_destiny_state(message: DestinySwitchMessage):
    """Updates the state of a destiny point."""
    with Session(engine) as session:
        destiny_state = session.exec(
            select(DestinyState).where(
                DestinyState.group_name == message.group_name,
                DestinyState.id == message.point_id,
            )
        ).first()
        if not destiny_state:
            raise ValueError(
                f"No state found for {message.group_name} and {message.point_id}"
            )
        destiny_state.is_light = not message.was_light
        session.commit()
    return message

async def delete_destiny_state(message: DestinyRemoveMessage):
    """Deletes a destiny point."""
    with Session(engine) as session:
        destiny_state = session.exec(
            select(DestinyState).where(
                DestinyState.group_name == message.group_name,
                DestinyState.id == message.point_id,
            )
        ).first()
        if not destiny_state:
            raise ValueError(
                f"No state found for {message.group_name} and {message.point_id}"
            )
        session.delete(destiny_state)
        session.commit()
#+

#+ HISTORY
def get_history(group_name: str, session: Session):
    """Gets the history of a group."""
    return session.exec(
        select(HistoryEvent)
        .where(HistoryEvent.group_name == group_name)
        .order_by(HistoryEvent.created_at.desc())
    ).all()


async def store_history_event(message: Type[JediMessage]):
    """Stores a historical event in the database."""
    print("Storing history event", message.to_json())
    with Session(engine) as session:
        new_event = HistoryEvent(
            group_name=message.group_name,
            created_at=datetime.now(),
            event_type=message.message_type,
            event_data=message.to_json(),
        )
        session.add(new_event)
        session.commit()
    return message
#+

#+ CHARACTER
def get_character_states(group_name: str, session: Session):
    """Gets the current state of a character."""
    return session.exec(
        select(CharacterState).where(CharacterState.group_name == group_name)
    ).all()

async def create_character_state(message: CharacterCreateMessage):
    """Creates a new character state."""
    with Session(engine) as session:
        if existing := session.exec( select(CharacterState).where( CharacterState.group_name == message.group_name, CharacterState.char_name == message.char_name, ) ).first():
            for key in existing.model_dump():
                setattr(existing, key, getattr(message, key))
            session.commit()
            return message # TODO MAYBE mark as updated?
        new_state = CharacterState(**message.__dict__)
        session.add(new_state)
        session.commit()
    return message

async def update_character_state(message: CharacterUpdateMessage):
    """Updates the state of a character."""
    with Session(engine) as session:
        character_state = session.exec(
            select(CharacterState).where(
                CharacterState.group_name == message.group_name,
                CharacterState.char_name == message.char_name,
            )
        ).first()
        if not character_state:
            raise ValueError(
                f"No state found for {message.group_name} and {message.char_name}"
            )
        setattr(character_state, message.trait_name, message.trait_value)
        session.commit()
    return message

async def delete_character_state(message: CharacterDeleteMessage):
    """Deletes a character state."""
    with Session(engine) as session:
        character_state = session.exec(
            select(CharacterState).where(
                CharacterState.group_name == message.group_name,
                CharacterState.char_name == message.char_name,
            )
        ).first()
        if not character_state:
            raise ValueError(
                f"No state found for {message.group_name} and {message.char_name}"
            )
        session.delete(character_state)
        session.commit()
    return message
