from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column, String

from app.db import Base


class BillingRequest(Base):
    __tablename__ = 'billing_requests'

    booking_id = Column(String, primary_key=True, unique=True, index=True)
    status = Column(String, default='pending')


class AMQPMessage(BaseModel):
    id: str
    content: Any
