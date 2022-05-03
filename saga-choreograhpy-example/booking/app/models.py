from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

class BaseModelMixin(SQLModel):
    __table_args__ = {'schema': 'booking_schema'}


class Booking(BaseModelMixin, table=True):
    uuid: UUID = Field(default=str(uuid4()), primary_key=True)
    desc: str
    status: str = Field(default='created')


class AMQPMessage(BaseModel):
    id: str
    content: Any
