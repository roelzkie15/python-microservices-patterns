from typing import Any, Dict

from attrs import define
from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from app.db import ProjectorBase


class DictMixin:
    def to_dict(self) -> Dict:
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


class Booking(DictMixin, ProjectorBase):
    """This is a projector class. We persist data through the event store."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    domain_uuid = Column(String, nullable=False, unique=True)

    status = Column(String, nullable=False, server_default="created")
    parking_slot_ref_no = Column(String, nullable=True)


@define
class AMQPMessage:
    id: str
    content: Any
