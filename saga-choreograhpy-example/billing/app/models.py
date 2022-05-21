from email.policy import default
from enum import unique
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column, Integer, Numeric, String

from app.db import Base


class BillingRequest(Base):
    __tablename__ = 'billing_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(Numeric(precision=12, scale=2), nullable=True)
    status = Column(String, default='pending')

    reference_no = Column(String, unique=True, nullable=False)

class AMQPMessage(BaseModel):
    id: str
    content: Any
