from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer

from app.db import Base


class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    status = Column(String, nullable=False, server_default='created')

    parking_slot_ref_no = Column(String, nullable=True)


class AMQPMessage(BaseModel):
    id: str
    content: Any
