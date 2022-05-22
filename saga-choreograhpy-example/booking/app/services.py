from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db import Session
from app.models import Booking


async def booking_details(session: Session, uuid: str) -> Booking:
    return session.query(Booking).filter(Booking.uuid == uuid).one()


async def booking_list(session: Session) -> List[Booking]:
    return session.query(Booking).all()


async def create_booking(session: Session, description: str) -> Booking:
    booking = Booking(uuid=str(uuid4()), description=description)
    session.add(booking)
    session.commit()
    session.refresh(booking)

    return booking
