from typing import List
from uuid import uuid4

from app.db import Session
from app.models import ParkingSlot, ParkingSlotReplica
from app.producers import replicate_parking_slot


async def create_parking_slot(session: Session, **kwargs) -> ParkingSlot:
    ps = ParkingSlot(uuid=str(uuid4()))

    {setattr(ps, k, v) for k, v in kwargs.items()}

    await replicate_parking_slot(ps.to_dict())

    session.add(ps)
    session.commit()
    session.refresh(ps)
    return ps


async def parking_slot_list(session: Session) -> List[ParkingSlot]:
    return session.query(ParkingSlot).all()


async def parking_slot_details(session: Session, uuid: str) -> ParkingSlot:
    return session.query(ParkingSlot).filter(ParkingSlot.uuid == uuid).one()


async def create_parking_slot_replica(session: Session, **kwargs) -> ParkingSlot:
    ps = ParkingSlotReplica(uuid=str(uuid4()))

    {setattr(ps, k, v) for k, v in kwargs.items()}

    session.add(ps)
    session.commit()
    session.refresh(ps)
    return ps
