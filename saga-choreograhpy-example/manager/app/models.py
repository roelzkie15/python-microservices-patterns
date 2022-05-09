from email.policy import default
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field

from app.db import SQLModel


class BookingRequest(SQLModel, table=True):
    booking_id: UUID = Field(default=None, primary_key=True)
    approved: bool = Field(default=True)


class AMQPMessage(BaseModel):
    id: str
    content: Any
