from typing import List
from uuid import uuid4

from aio_pika import IncomingMessage

from app.db import Session
from app.models import Booking


async def booking_details(uuid: str) -> Booking:
    with Session() as session:
        return session.query(Booking).filter(Booking.uuid == uuid).one()


async def booking_list() -> List[Booking]:
    with Session() as session:
        return session.query(Booking).all()


async def create_booking(description: str) -> Booking:
    with Session() as session:
        booking = Booking(uuid= str(uuid4()), description=description)

        session.add(booking)
        session.commit()
        session.refresh(booking)

        return booking


async def test_consume(message: IncomingMessage) -> None:
    print('test consume: ', message.body.decode())

    await message.ack()
