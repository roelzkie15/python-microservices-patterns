from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Booking(SQLModel, table=True):
    uuid: UUID = Field(default=str(uuid4()), primary_key=True)
    desc: str
    status: str = Field(default='created')


class AMQPMessage(BaseModel):
    id: str
    content: Any
