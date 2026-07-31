"""Pydantic domain models produced by database extraction."""

from datetime import datetime
from pydantic import BaseModel, Field


class Contact(BaseModel):
    id: int | str
    name: str
    username: str | None = None


class Message(BaseModel):
    id: int | str
    chat_id: int | str
    text: str
    date: datetime | None = None
    sender: Contact | None = None


class Chat(BaseModel):
    id: int | str
    title: str
    messages: list[Message] = Field(default_factory=list)
