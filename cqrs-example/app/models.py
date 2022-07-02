from typing import Dict

from app.db import Base, ReplicaBase
from sqlalchemy import Column, String


class DictMixin:
    def to_dict(self) -> Dict:
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


class ParkingSlot(DictMixin, Base):
    __tablename__ = "parking_slots"

    uuid = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String, nullable=False)

    # available/blocked/reserved
    status = Column(String, nullable=False, server_default="available")


class ParkingSlotReplica(DictMixin, ReplicaBase):
    __tablename__ = "parking_slots"

    uuid = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String, nullable=False)

    # available/blocked/reserved
    status = Column(String, nullable=False, server_default="available")
