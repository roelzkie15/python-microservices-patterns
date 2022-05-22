from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column, String

from app.db import Base


class Booking(Base):
    __tablename__ = 'bookings'

    uuid = Column(String, primary_key=True, unique=True, index=True)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default='created')

    parking_space_uuid = Column(String, nullable=True)


class AMQPMessage(BaseModel):
    id: str
    content: Any
