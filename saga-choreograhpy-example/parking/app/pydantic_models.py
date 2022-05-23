from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from app.models import ParkingSlot

PydanticParkingSlot = sqlalchemy_to_pydantic(ParkingSlot)
