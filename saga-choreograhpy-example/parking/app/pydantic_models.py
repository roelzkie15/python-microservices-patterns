from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from app.models import BookingRequest

PydanticBookingRequest = sqlalchemy_to_pydantic(BookingRequest)
