from typing import List
from uuid import UUID

from sqlmodel import Session, select

from app.db import engine
from app.models import Booking


async def booking_details(uuid: str) -> Booking:
    with Session(engine) as session:
        statement = select(Booking).where(Booking.uuid == UUID(uuid))
        results = session.exec(statement)
        return results.one()


async def booking_list() -> List[Booking]:
    with Session(engine) as session:
        statement = select(Booking)
        results = session.exec(statement)
        return results.all()


async def create_booking(desc: str) -> Booking:
    with Session(engine) as session:
        booking = Booking(desc=desc)

        session.add(booking)
        session.commit()
        session.refresh(booking)

        return booking


async def test_consume(message_body: bytes) -> None:
    print('test consume: ', message_body.decode())
