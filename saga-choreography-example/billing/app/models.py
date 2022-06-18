from decimal import Decimal
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.db import Base


class DictMixin:

    def to_dict(self):
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


class BillingRequest(Base, DictMixin):
    __tablename__ = 'billing_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(Numeric(precision=12, scale=2), nullable=True)
    status = Column(String, default='pending')

    reference_no = Column(String, unique=True, nullable=False)

    payment_reconciliations = relationship(
        'PaymentReconciliation',
        backref='billing_request',
    )

    @hybrid_property
    def total_paid(self):
        return Decimal(sum([payment.amount for payment in self.payment_reconciliations]))

    @hybrid_property
    def balance(self):
        return Decimal(self.total - self.total_paid)

    def calculate_total_payment(self, amount: Decimal) -> Decimal:
        '''
        Sum of total payment including incoming payment.
        '''
        return Decimal(amount + self.total_paid)


class PaymentReconciliation(Base, DictMixin):
    __tablename__ = 'payment_reconciliations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)

    billing_request_id = Column(Integer, ForeignKey('billing_requests.id'))


class AMQPMessage(BaseModel):
    id: str
    content: Any
