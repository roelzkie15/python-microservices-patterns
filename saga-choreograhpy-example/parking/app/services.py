import ast
from typing import List

from aio_pika import IncomingMessage
from sqlalchemy.sql import exists

from app import logging
from app.db import Session
from app.models import BookingRequest


async def create_booking_request_from_event(message: IncomingMessage):
    decoded_message = ast.literal_eval(str(message.body.decode()))

    logging.info(f'Received message {str(decoded_message)}')

    # A message should be idempotent.
    is_exists = await booking_request_exists(decoded_message['id'])
    if is_exists:
        logging.warning(f'Booking ID: {decoded_message["id"]} already exist.')
        return

    booking_request = await create_booking_request(decoded_message['id'])

    logging.info(
        f'New booking request was created from event store - {booking_request.booking_id}')

    return booking_request


async def create_booking_request(booking_id: str) -> BookingRequest:
    with Session() as session:
        booking = BookingRequest(booking_id=booking_id)

        session.add(booking)
        session.commit()
        session.refresh(booking)

        return booking


async def booking_request_exists(uuid: str) -> BookingRequest:
    with Session() as session:
        return session.query(exists().where(BookingRequest.booking_id == uuid)).scalar()


async def booking_request_details(uuid: str) -> BookingRequest:
    with Session() as session:
        return session.query(BookingRequest).filter(BookingRequest.booking_id==uuid).one()


async def booking_request_list() -> List[BookingRequest]:
    with Session() as session:
        return session.query(BookingRequest).all()

async def approve_booking_request(booking_request: BookingRequest) -> BookingRequest:
    with Session() as session:
        booking_request.approved = True
        session.add(booking_request)
        session.commit()
        session.refresh(booking_request)

        return booking_request
