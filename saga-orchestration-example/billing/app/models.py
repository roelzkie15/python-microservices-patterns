from typing import Any, Dict

from pydantic import BaseModel
from sqlalchemy import Column, Integer, Numeric, String

from app.db import Base


class DictMixin:
    def to_dict(self) -> Dict:
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


class BillingRequest(Base, DictMixin):
    __tablename__ = 'billing_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(Numeric(precision=12, scale=2), nullable=True)
    status = Column(String, default='pending')

    # Must be <booking.id>:<parking.uuid>
    reference_no = Column(String, unique=True, nullable=False)


class CommandResponse(BaseModel):
    content: Any | None = None
    reply_state: str | None = None
