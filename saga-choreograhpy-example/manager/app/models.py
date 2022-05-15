from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column, String

from app.db import Base


class BookingRequest(Base):
    __tablename__ = 'booking_request'

    booking_id = Column(String, primary_key=True, unique=True, index=True)
    approved = Column(String, nullable=False, default=False)


class AMQPMessage(BaseModel):
    id: str
    content: Any
