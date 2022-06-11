
from typing import List
from uuid import uuid4

from app.db import Session
from app.models import ParkingSlot


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
