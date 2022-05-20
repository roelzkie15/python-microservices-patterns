import ast
from decimal import Decimal
from typing import List

from aio_pika import IncomingMessage

from app import logging
from app.db import Session
from app.models import BillingRequest


async def create_billing_request_from_event(message: IncomingMessage):
    decoded_message = ast.literal_eval(str(message.body.decode()))
    logging.info(f'Received message {str(decoded_message)}')

    br = await create_billing_request(decoded_message['id'])

    logging.info(f'Booking request with ID {br.booking_id} was created!')

    return br


async def create_billing_request(uuid: str, total: Decimal = Decimal('100.00')) -> BillingRequest:
    with Session() as session:
        br = BillingRequest(booking_id=uuid, total=total)
        session.add(br)
        session.commit()
        session.refresh(br)

        return br


async def billing_request_list() -> List[BillingRequest]:
    with Session() as session:
        return session.query(BillingRequest).all()


async def billing_request_details(uuid: str) -> BillingRequest:
    with Session() as session:
        return session.query(BillingRequest).filter(BillingRequest.booking_id == uuid).one()
