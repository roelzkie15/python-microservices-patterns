import json
import ast
from typing import List
from uuid import uuid4

from aio_pika import IncomingMessage

from app.amqp_client import AMQPClient
from app.db import Session
from app.models import AMQPMessage, ParkingSlot


async def update_parking_slot(session: Session, ps: ParkingSlot) -> ParkingSlot:
    session.commit()
    session.refresh(ps)
    return ps


async def create_parking_slot(session: Session, **kwargs) -> ParkingSlot:
    ps = ParkingSlot(uuid=str(uuid4()))

    {setattr(ps, k, v) for k, v in kwargs.items()}

    session.add(ps)
    session.commit()
    session.refresh(ps)
    return ps


async def parking_slot_list(session: Session) -> List[ParkingSlot]:
    return session.query(ParkingSlot).all()


async def parking_slot_details(session: Session, uuid: str) -> ParkingSlot:
    return session.query(ParkingSlot).filter(ParkingSlot.uuid == uuid).one()


async def block_parking_slot(session: Session, uuid: str) -> bool:
    ps = await parking_slot_details(session, uuid)

    if ps.status != 'available':
        return False

    ps.status = 'blocked'
    ps = await update_parking_slot(session, ps)

    return ps.status == 'blocked'


async def unblock_parking_slot(session: Session, uuid: str) -> bool:
    ps = await parking_slot_details(session, uuid)
    ps.status = 'available'
    ps = await update_parking_slot(session, ps)
    return ps.status == 'available'


async def reserve_parking_slot(session: Session, uuid: str) -> bool:
    ps = await parking_slot_details(session, uuid)
    ps.status = 'reserved'
    ps = await update_parking_slot(session, ps)
    return ps.status == 'reserved'


async def parking_command_event_processor(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        command = message.headers.get('COMMAND')
        client = message.headers.get('CLIENT')

        booking = json.loads(str(message.body.decode('utf-8')))
        parking_slot_uuid = booking.get('parking_slot_ref_no').split(':')[0]
        response_obj: AMQPMessage = None

        if client == 'BOOKING_REQUEST_ORCHESTRATOR' and command == 'PARKING_BLOCK':
            with Session() as session:
                is_available = await block_parking_slot(session, parking_slot_uuid)
                await message.ack()
                response_obj = AMQPMessage(
                    id=message.correlation_id,
                    reply_state=(
                        'PARKING_UNAVAILABLE', 'PARKING_AVAILABLE'
                    )[is_available]
                )

        if client == 'BOOKING_REQUEST_ORCHESTRATOR' and command == 'PARKING_UNBLOCK':
            with Session() as session:
                is_unblock = await unblock_parking_slot(session, parking_slot_uuid)
                await message.ack()
                response_obj = AMQPMessage(
                    id=message.correlation_id,
                    reply_state=('PARKING_BLOCKED', 'PARKING_UNBLOCKED')[
                        is_unblock]
                )

        if client == 'BOOKING_REQUEST_ORCHESTRATOR' and command == 'PARKING_RESERVE':
            with Session() as session:
                is_reserved = await reserve_parking_slot(session, parking_slot_uuid)

                # NOTE: Comment the above line and uncomment this line to trigger
                # compensation transaction.
                # is_reserved = False

                await message.ack()
                response_obj = AMQPMessage(
                    id=message.correlation_id,
                    reply_state=(
                        'PARKING_RESERVATION_FAILED', 'PARKING_RESERVED'
                    )[is_reserved]
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
