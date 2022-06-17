
import ast
import json
from typing import List

from aio_pika import IncomingMessage

from app.amqp_client import AMQPClient
from app.db import Session
from app.models import AMQPMessage, BillingRequest


async def create_billing_request(session: Session, reference_no: str) -> BillingRequest:
    br = BillingRequest(
        # Default total to 100.00
        total=100.0,
        reference_no=reference_no,
        status='paid'
    )
    session.add(br)
    session.commit()
    session.refresh(br)

    return br


async def billing_request_update(session: Session, br: BillingRequest) -> BillingRequest:
    session.commit()
    session.refresh(br)
    return br


async def billing_request_details_by_reference_no(session: Session, reference_no: str) -> BillingRequest:
    return session.query(BillingRequest).filter(BillingRequest.reference_no == reference_no).one()


async def billing_request_list(session: Session) -> List[BillingRequest]:
    return session.query(BillingRequest).all()


async def billing_command_event_processor(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        command = message.headers.get('COMMAND')
        client = message.headers.get('CLIENT')

        booking = json.loads(str(message.body.decode('utf-8')))
        response_obj: AMQPMessage = None
        if client == 'BOOKING_REQUEST_ORCHESTRATOR' and command == 'BILLING_PAY':
            with Session() as session:
                await create_billing_request(session, booking.get("parking_slot_ref_no"))

                await message.ack()
                response_obj = AMQPMessage(
                    id=message.correlation_id,
                    content=None,
                    reply_state='BILL_PAID'
                )

        if client == 'BOOKING_REQUEST_ORCHESTRATOR' and command == 'BILLING_REFUND':
                with Session() as session:
                    br = await billing_request_details_by_reference_no(session, booking.get("parking_slot_ref_no"))

                    br.status = 'refunded'
                    await billing_request_update(session, br)
                    await message.ack()

                    response_obj = AMQPMessage(
                        id=message.correlation_id,
                        content=None
                    )

        # There must be a response object to signal orchestrator of
        # the outcome of the request.
        assert response_obj is not None

        amqp_client: AMQPClient = await AMQPClient().init()
        await amqp_client.event_producer(
            'BOOKING_TX_EVENT_STORE',
            message.reply_to,
            message.correlation_id,
            response_obj
        )
        await amqp_client.connection.close()
