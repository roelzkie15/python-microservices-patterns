import ast
from typing import List
from uuid import uuid4

from aio_pika import IncomingMessage
from sqlalchemy.orm import Session

from app import logging
from app.db import Session
from app.models import Booking


async def set_booking_to_status_from_event(message: IncomingMessage):
    decoded_message = ast.literal_eval(str(message.body.decode()))

    with Session() as session:
        booking = await booking_details_by_parking_ref_no(session, decoded_message['id'])

        if decoded_message['content']['status'] == 'unavailable':
            booking.status = 'failed'
        else:
            # reserved.
            booking.status = 'done'

        await update_booking(session, booking)

    logging.info(f'Booking with ID {booking.id} was marked as {booking.status}!')

    return booking


async def booking_details(session: Session, id: str) -> Booking:
    return session.query(Booking).filter(Booking.id == id).one()


async def booking_details_by_parking_ref_no(session: Session, parking_slot_ref_no: str) -> Booking:
    return session.query(Booking).filter(Booking.parking_slot_ref_no == parking_slot_ref_no).one()


async def booking_list(session: Session) -> List[Booking]:
    return session.query(Booking).all()


async def create_booking(session: Session, parking_slot_uuid: str) -> Booking:
    # Since customers may happen to book the same parking slot,
    # we need to include unique booking identifier (uuid4) to parking_slot_ref_no.
    # The booking identifier will be used throughout the services to identify
    # transaction.
    booking = Booking(parking_slot_ref_no=f'{parking_slot_uuid}:{uuid4()}', status='pending')
    session.add(booking)
    session.commit()
    session.refresh(booking)

    return booking


async def update_booking(session: Session, booking: Booking) -> Booking:
    session.commit()
    session.refresh(booking)
    return booking
