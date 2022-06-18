from typing import Any, Dict

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer

from app.db import Base


class DictMixin:
    def to_dict(self) -> Dict:
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


class Booking(Base, DictMixin):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    status = Column(String, nullable=False, server_default='created')

    parking_slot_ref_no = Column(String, nullable=True)


class AMQPMessage(BaseModel):
    id: str
    content: Any
