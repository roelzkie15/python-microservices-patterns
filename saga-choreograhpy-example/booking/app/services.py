from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db import Session
from app.models import Booking


async def booking_details(session: Session, id: str) -> Booking:
    return session.query(Booking).filter(Booking.id == id).one()


async def booking_list(session: Session) -> List[Booking]:
    return session.query(Booking).all()


async def create_booking(session: Session, parking_slot_uuid: str) -> Booking:
    booking = Booking(parking_slot_uuid=parking_slot_uuid)
    session.add(booking)
    session.commit()
    session.refresh(booking)

    return booking
