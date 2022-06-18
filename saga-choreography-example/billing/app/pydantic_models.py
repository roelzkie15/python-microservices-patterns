from typing import List

from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from app.models import BillingRequest, PaymentReconciliation

PydanticBillingRequest = sqlalchemy_to_pydantic(BillingRequest)
PydanticPaymentReconciliation = sqlalchemy_to_pydantic(PaymentReconciliation)


class PydanticBillingRequestWithPaymentReconciliation(PydanticBillingRequest):
    payment_reconciliations: List[PydanticPaymentReconciliation]
