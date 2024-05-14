"""This module contains the functions that interact with the database."""

from datetime import datetime
from typing import Type
import random
import json

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
    RollResultMessage,
    RollReqestMessage,
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
#+

#+ ROLL
async def roll_dice(message: RollReqestMessage):
    """Rolls dice for a character."""
    dice_definitions = {
    'proficiency' : [
        "success_success",
        "success_success",
        "success",
        "success",
        "advantage_advantage",
        "advantage_advantage",
        "advantage",
        "success_advantage",
        "success_advantage",
        "success_advantage",
        "triumph",
        "empty",
    ],
    'ability' : [
        "success",
        "success",
        "success_success",
        "advantage",
        "advantage",
        "advantage_advantage",
        "success_advantage",
        "empty",
    ],
    'boost' : [
        "success",
        "advantage",
        "success_advantage",
        "advantage_advantage",
        "empty",
        "empty",
    ],
    'challenge' : [
        "failure",
        "failure",
        "failure_failure",
        "failure_failure",
        "threat",
        "threat",
        "threat_threat",
        "threat_threat",
        "failure_threat",
        "failure_threat",
        "despair",
        "empty",
    ],
    'difficulty' : [
        "failure",
        "failure_failure",
        "threat",
        "threat",
        "threat",
        "threat_threat",
        "failure_threat",
        "empty",
    ],
    'setback' : [
        "failure",
        "failure",
        "threat",
        "threat",
        "empty",
        "empty",
    ],
    'force' : [
        "dark",
        "dark",
        "dark",
        "dark",
        "dark",
        "dark",
        "dark_dark",
        "light",
        "light",
        "light_light",
        "light_light",
        "light_light",
    ]}
    results:dict[str,list[str]] ={
        dice: [random.choice(dice_definitions.get(dice,[dice])) for _ in range(count)]
        for dice, count in json.loads(message.dice_pool).items()
    }
    return  RollResultMessage(
        group_name=message.group_name,
        char_name=message.char_name,
        author=message.author,
        dice_pool=message.dice_pool,
        result=json.dumps(results),
        comment=message.comment,
    )

