import ast
from typing import List

from aio_pika import IncomingMessage
from sqlalchemy.orm import Session

from app import logging
from app.db import Session
from app.models import Booking


async def set_booking_to_done_on_reserved(message: IncomingMessage):
    decoded_message = ast.literal_eval(str(message.body.decode()))
    logging.info(f'Received message {str(decoded_message)}')

    with Session() as session:
        booking = await booking_details_by_parking_slot_uuid(session, decoded_message['id'])
        booking.status = 'done'

        await update_booking(session, booking)

    logging.info(f'Booking with ID {booking.id} was marked as done!')

    return booking


async def booking_details(session: Session, id: str) -> Booking:
    return session.query(Booking).filter(Booking.id == id).one()


async def booking_details_by_parking_slot_uuid(session: Session, uuid: str) -> Booking:
    return session.query(Booking).filter(Booking.parking_slot_uuid == uuid).one()


async def booking_list(session: Session) -> List[Booking]:
    return session.query(Booking).all()


async def create_booking(session: Session, parking_slot_uuid: str) -> Booking:
    booking = Booking(parking_slot_uuid=parking_slot_uuid)
    session.add(booking)
    session.commit()
    session.refresh(booking)

    return booking


async def update_booking(session: Session, booking: Booking) -> Booking:
    session.commit()
    session.refresh(booking)
    return booking
