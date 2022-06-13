
import ast
from typing import List
from uuid import uuid4

from aio_pika import IncomingMessage

from app.db import Session
from app.models import EventResponse, ParkingSlot


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


async def parking_reserve_from_saga_event(session: Session, message: IncomingMessage) -> EventResponse:
    booking = ast.literal_eval(message.body.decode('utf-8'))
    parking_slot_uuid = booking.get('parking_slot_ref_no').split(':')[0]
    is_available = await block_parking_slot(session, parking_slot_uuid)

    await message.ack()

    return EventResponse(
        content=None,
        reply_state=('PARKING_UNAVAILABLE', 'PARKING_AVAILABLE')[is_available]
    )


async def parking_unblock_from_saga_event(session: Session, message: IncomingMessage) -> EventResponse:
    booking = ast.literal_eval(message.body.decode('utf-8'))
    parking_slot_uuid = booking.get('parking_slot_ref_no').split(':')[0]
    is_unblock = await unblock_parking_slot(session, parking_slot_uuid)

    await message.ack()

    return EventResponse(
        content=None,
        reply_state=('PARKING_BLOCKED', 'PARKING_UNBLOCKED')[is_unblock]
    )
