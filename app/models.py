"""
This file contains the models for the database.
"""

import json
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine

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


class DestinyState(SQLModel, table=True):
    """Each Group can has multiple Destiny Points, this class represents the state of a single Destiny Point for a specific Group."""

    id: int = Field(primary_key=True)
    group_name: str = Field(primary_key=True)
    is_light: bool


class HistoryEvent(SQLModel, table=True):
    """Log of all events that happened in a Group. This can be used to display the history of the Group."""

    id: Optional[int] = Field(primary_key=True, default=None)
    group_name: str
    created_at: datetime
    event_type: str
    event_data: str

    @property
    def json_data(self):
        '''Converts the event_data to a JSON object'''
        return json.loads(self.event_data)

    @property
    def display(self):
        '''Returns a string representation of the event'''
        return f'{self.created_at.strftime("%H:%M:%S")}: {self.event_type} - {self.event_data}'


SQL_FILE_NAME = "database.db"
sqlite_url = f"sqlite:///{SQL_FILE_NAME}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables():
    """Creates the database and tables if they don't exist"""
    SQLModel.metadata.create_all(engine, checkfirst=True)
