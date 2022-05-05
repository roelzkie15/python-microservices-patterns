from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field

from app.db import SQLModel


class Booking(SQLModel, table=True):
    uuid: UUID = Field(default=None, primary_key=True)
    desc: str
    status: str = Field(default='created')


class AMQPMessage(BaseModel):
    id: str
    content: Any
