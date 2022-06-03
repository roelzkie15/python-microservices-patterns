from typing import Any

from sqlalchemy import Column, String

from app.db import Base


class ParkingSlot(Base):
    __tablename__ = 'parking_slots'

    uuid = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String, nullable=False)

    status = Column(String, nullable=False, server_default='pending')
