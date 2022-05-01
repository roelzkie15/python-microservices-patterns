from typing import List

from sqlmodel import Session
from strawberry.types import Info

from app.db import engine
from app.mocks import BOOKING_LIST
from app.models import Booking


async def booking_details(uuid: str) -> Booking:
    return [booking for booking in BOOKING_LIST if booking.uuid == uuid][0]


async def booking_list() -> List[Booking]:
    return BOOKING_LIST


async def create_booking(desc: str) -> Booking:
    with Session(engine) as session:
        booking = Booking(desc=desc)

        session.add(booking)
        session.commit()
        session.refresh(booking)

        return booking

async def test_consume(message_body: bytes) -> None:
    print('test consume: ', message_body.decode())
