import ast
from typing import List
from uuid import uuid4

from aio_pika import IncomingMessage

from app import logging
from app.amqp_client import AMQPClient
from app.db import Session
from app.models import AMQPMessage, ParkingSlot


async def update_parking_slot_to_reserved_by_ref_no(message: IncomingMessage) -> ParkingSlot:
    decoded_message = ast.literal_eval(str(message.body.decode()))

    with Session() as session:
        reference_no = decoded_message['id']

        # Get the parking-slot identifier only.
        parking_slot_uuid = reference_no.split(':')[0]
        ps = await parking_slot_details(session, parking_slot_uuid)

        amqp_client: AMQPClient = await AMQPClient().init()

        # If status is already reserved.
        if ps.status == 'reserved':
            await amqp_client.event_producer(
                'BOOKING_TX_EVENT_STORE', 'parking.unavailable',
                message=AMQPMessage(
                    id=reference_no,
                    content={'status': 'unavailable'}
                )
            )
            await amqp_client.connection.close()
            logging.info(f'Parking slot with UUID {ps.uuid} is unavailable!')
            return None

        ps.status = 'reserved'
        ps = await update_parking_slot(session, ps)

        amqp_client: AMQPClient = await AMQPClient().init()
        await amqp_client.event_producer(
            'BOOKING_TX_EVENT_STORE', 'parking.reserved',
            message=AMQPMessage(
                id=reference_no, content={'status': 'reserved'}
            )
        )
        await amqp_client.connection.close()

    logging.info(f'Parking slot with UUID {ps.uuid} has been reserved!')

    return ps


async def update_parking_slot(session: Session, ps: ParkingSlot) -> ParkingSlot:
    session.commit()
    session.refresh(ps)
    return ps


async def create_parking_slot(session: Session, **kwargs) -> ParkingSlot:
    ps = ParkingSlot(uuid=str(uuid4()))

    {setattr(ps, k, v) for k,v in kwargs.items()}

    session.add(ps)
    session.commit()
    session.refresh(ps)
    return ps


async def parking_slot_list(session: Session) -> List[ParkingSlot]:
    return session.query(ParkingSlot).all()


async def parking_slot_details(session: Session, uuid: str) -> ParkingSlot:
    return session.query(ParkingSlot).filter(ParkingSlot.uuid == uuid).one()
