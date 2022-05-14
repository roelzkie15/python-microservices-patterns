from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column, String

from app.db import Base


class Booking(Base):
    __tablename__ = 'booking'

    uuid = Column(String, primary_key=True, unique=True, index=True)
    desc = Column(String)
    status = Column(String, nullable=False, default='created')


class AMQPMessage(BaseModel):
    id: str
    content: Any
