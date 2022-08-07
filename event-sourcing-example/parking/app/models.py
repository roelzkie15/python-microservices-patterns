from typing import Any, Dict

from sqlalchemy import Column, String

from app.db import Base
from pydantic import BaseModel


class DictMixin:
    def to_dict(self) -> Dict:
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


class ParkingSlot(Base, DictMixin):
    __tablename__ = 'parking_slots'

    uuid = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String, nullable=False)

    # available/blocked/reserved
    status = Column(String, nullable=False, server_default='available')


class AMQPMessage(BaseModel):
    id: str
    content: Any | None = None
    reply_state: str | None = None
