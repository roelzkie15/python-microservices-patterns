import ast

from aio_pika import IncomingMessage

from app import logging
from app.models import BillingRequest
from app.db import Session


async def create_billing_request_from_event(message: IncomingMessage):
    decoded_message = ast.literal_eval(str(message.body.decode()))
    logging.info(f'Received message {str(decoded_message)}')

    br = await create_billing_request(decoded_message['id'])

    logging.info(f'Booking request with ID {br.booking_id} was created!')

    return br

async def create_billing_request(uuid: str) -> BillingRequest:
    with Session() as session:
        br = BillingRequest(booking_id=uuid)
        session.add(br)
        session.commit()
        session.refresh(br)

        return br
