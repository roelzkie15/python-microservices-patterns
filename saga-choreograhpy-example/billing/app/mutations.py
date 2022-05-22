from decimal import Decimal

import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.amqp_client import AMQPClient
from app.models import AMQPMessage
from app.object_types import (BillingAlreadyPaidError, PayBillActionResponse,
                              PaymentOverError, PydanticBillingRequest,
                              PydanticPaymentReconciliation)
from app.services import (billing_request_details_by_reference_no,
                          create_payment_reconciliation,
                          update_billing_request)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def pay_bill(self, reference_no: str, amount: Decimal, info: Info) -> PayBillActionResponse:
        session: Session = info.context['request'].app.state.session

        billing_request = await billing_request_details_by_reference_no(session, ref_no=reference_no)

        if billing_request.status == 'paid':
            return BillingAlreadyPaidError

        # To avoid complex logic we will only accept sufficient payment.
        total_payment = billing_request.calculate_total_payment(amount)
        if total_payment > billing_request.total:
            return PaymentOverError(
                message=f'Payment is over {total_payment - billing_request.total}.\nUnable to process payment transaction.'
            )

        reconciliation = await create_payment_reconciliation(
            session, billing_request.id, amount
        )
        pydantic_reconciliation = PydanticPaymentReconciliation.from_orm(
            reconciliation
        )

        if billing_request.balance == Decimal('0.0'):
            billing_request.status = 'paid'
            billing_request = await update_billing_request(session, billing_request)

            pydantic_billing_request = PydanticBillingRequest.from_orm(
                billing_request)

            amqp_client: AMQPClient = info.context['request'].app.state.amqp_client
            await amqp_client.event_producer(
                'BOOKING_TX_EVENT_STORE', 'bill.paid', message=AMQPMessage(id=str(billing_request.id), content=pydantic_billing_request.dict())
            )

        return pydantic_reconciliation
