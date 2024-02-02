from typing import Dict

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(default='User')
    style: str = Field(default='Classic')
    color: str = Field(default='Auto')
    accent: str = Field(default='Auto')
    token: Dict[str, str] = Field(default={}, sa_column=Column(JSON))


class Track(BaseModel):
    name: str
    album: str
    artist: str
    duration: int
    position: int
    artwork: str
    url: str
    raw: dict


class Stats(BaseModel):
    raw: dict

