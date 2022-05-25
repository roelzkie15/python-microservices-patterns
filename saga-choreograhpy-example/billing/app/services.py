import ast
from decimal import Decimal
from typing import List

from aio_pika import IncomingMessage
from sqlalchemy.orm import Session

from app import logging
from app.models import BillingRequest, PaymentReconciliation
from app.db import Session


async def create_billing_request_from_event(message: IncomingMessage):
    decoded_message = ast.literal_eval(str(message.body.decode()))

    with Session() as session:
        br = await create_billing_request(session, decoded_message['id'])

    logging.info(f'Billing request with ID {br.id} was created!')

    return br


async def set_billing_request_status_from_event(message: IncomingMessage):
    decoded_message = ast.literal_eval(str(message.body.decode()))

    with Session() as session:
        br = await billing_request_details_by_reference_no(session, decoded_message['id'])

        if decoded_message['content']['status'] == 'unavailable':
            br.status = 'refunded'
            await update_billing_request(session, br)

    logging.info(f'Billing request with ID {br.id} was {br.status}!')

    return br


async def create_billing_request(session: Session, uuid: str, total: Decimal = Decimal('100.00')) -> BillingRequest:
    '''
    Assuming all billing request total is cost $100.00
    '''
    br = BillingRequest(reference_no=uuid, total=total)
    session.add(br)
    session.commit()
    session.refresh(br)

    return br


async def update_billing_request(session: Session, br: BillingRequest) -> BillingRequest:
    session.commit()
    session.refresh(br)
    return br


async def billing_request_list(session: Session) -> List[BillingRequest]:
    return session.query(BillingRequest).all()


async def billing_request_details(session: Session, id: int) -> BillingRequest:
    return session.query(BillingRequest).filter(BillingRequest.id == id).one()


async def billing_request_details_by_reference_no(session: Session, ref_no: str) -> BillingRequest:
    return session.query(BillingRequest).filter(BillingRequest.reference_no == ref_no).one()


async def create_payment_reconciliation(session: Session, billing_request_id: int, amount: Decimal) -> PaymentReconciliation:
    pr = PaymentReconciliation(
        billing_request_id=billing_request_id,
        amount=amount
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)
    return pr


async def payment_reconciliation_list(session: Session) -> List[PaymentReconciliation]:
    return session.query(PaymentReconciliation).all()


async def payment_reconciliation_details(session: Session, id: int) -> List[PaymentReconciliation]:
    return session.query(PaymentReconciliation).filter(PaymentReconciliation.id == id).one()
