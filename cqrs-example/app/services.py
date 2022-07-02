import ast
import json
from typing import List
from uuid import uuid4

from app.db import Session
from app.models import ParkingSlot


async def create_parking_slot(session: Session, **kwargs) -> ParkingSlot:
    ps = ParkingSlot(uuid=str(uuid4()))

    {setattr(ps, k, v) for k, v in kwargs.items()}

    session.add(ps)
    session.commit()
    return ps


async def parking_slot_list(session: Session) -> List[ParkingSlot]:
    return session.query(ParkingSlot).all()


async def parking_slot_details(session: Session, uuid: str) -> ParkingSlot:
    return session.query(ParkingSlot).filter(ParkingSlot.uuid == uuid).one()
