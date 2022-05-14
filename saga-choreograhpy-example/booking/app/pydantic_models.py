from typing import List
from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from app.models import Booking

PydanticBooking = sqlalchemy_to_pydantic(Booking)
