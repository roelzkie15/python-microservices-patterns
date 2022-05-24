import ast
from typing import List
from uuid import uuid4

from aio_pika import IncomingMessage

from app import logging
from app.db import Session
from app.models import ParkingSlot


async def update_parking_slot_to_reserved_by_uuid(message: IncomingMessage) -> ParkingSlot:
    decoded_message = ast.literal_eval(str(message.body.decode()))
    logging.info(f'Received message {str(decoded_message)}')

    with Session() as session:
        ps = await parking_slot_details(session, decoded_message['id'])
        ps.status = 'reserved'

        ps = await update_parking_slot(session, ps)

    logging.info(f'Parking slot with UUID {ps.uuid} has been reserved!')

    return ps


async def update_parking_slot(session: Session, ps: ParkingSlot) -> ParkingSlot:
    session.commit()
    session.refresh(ps)
    return ps


async def create_parking_slot(session: Session, name: str) -> ParkingSlot:
    ps = ParkingSlot(uuid=str(uuid4()), name=name)
    session.add(ps)
    session.commit()
    session.refresh(ps)
    return ps


async def parking_slot_list(session: Session) -> List[ParkingSlot]:
    return session.query(ParkingSlot).all()


async def parking_slot_details(session: Session, uuid: str) -> ParkingSlot:
    return session.query(ParkingSlot).filter(ParkingSlot.uuid == uuid).one()
