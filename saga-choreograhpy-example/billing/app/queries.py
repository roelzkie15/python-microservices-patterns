
from typing import List

import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.object_types import (BillingRequestType,
                              BillingRequestWithReconciliationType,
                              PaymentReconciliationType)
from app.pydantic_models import (
    PydanticBillingRequest, PydanticBillingRequestWithPaymentReconciliation,
    PydanticPaymentReconciliation)
from app.services import (billing_request_details, billing_request_list,
                          payment_reconciliation_details,
                          payment_reconciliation_list)


@strawberry.type
class Query:

    @strawberry.field
    async def billing_request_details(self, id: int, info: Info) -> BillingRequestWithReconciliationType:
        session: Session = info.context['request'].app.state.session

        br = await billing_request_details(session, id)
        return PydanticBillingRequestWithPaymentReconciliation.from_orm(br)

    @strawberry.field
    async def billing_request_list(self, info: Info) -> List[BillingRequestType]:
        session: Session = info.context['request'].app.state.session

        br_list = await billing_request_list(session)
        return [PydanticBillingRequest.from_orm(br) for br in br_list]

    @strawberry.field
    async def payment_reconciliation_details(self, id: int, info: Info) -> PaymentReconciliationType:
        session: Session = info.context['request'].app.state.session

        pr = await payment_reconciliation_details(session, id)
        return PydanticPaymentReconciliation.from_orm(pr)

    @strawberry.field
    async def payment_reconciliation_list(self, info: Info) -> List[PaymentReconciliationType]:
        session: Session = info.context['request'].app.state.session

        pr_list = await payment_reconciliation_list(session)
        return [PydanticPaymentReconciliation.from_orm(pr) for pr in pr_list]
