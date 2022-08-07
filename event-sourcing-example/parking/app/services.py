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


async def reserve_parking_slot(session: Session, uuid: str) -> bool:
    ps = await parking_slot_details(session, uuid)
    ps.status = 'reserved'
    ps = await update_parking_slot(session, ps)
    return ps.status == 'reserved'


async def booking_event_processor(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        await message.ack()

        data = json.loads(str(message.body.decode('utf-8')))
        parking_slot_uuid = data.get("id")
        booking = data.get("content")

        if booking.get("status").lower() == "created":
            with Session() as session:
                await block_parking_slot(session, parking_slot_uuid)
        elif booking.get("status").lower() == "reserved":
            with Session() as session:
                await reserve_parking_slot(session, parking_slot_uuid)
