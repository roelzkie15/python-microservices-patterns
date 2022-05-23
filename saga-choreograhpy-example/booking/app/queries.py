
from typing import List

import strawberry
from strawberry.types import Info

from app.object_types import BookingType
from app.pydantic_models import PydanticBooking
from app.services import booking_details, booking_list
from sqlalchemy.orm import Session


@strawberry.type
class Query:
    @strawberry.field
    async def booking(self, id: str, info: Info) -> BookingType:
        session: Session = info.context['request'].app.state.session

        booking = await booking_details(session, id)
        return PydanticBooking.from_orm(booking)

    @strawberry.field
    async def bookings(self, info: Info) -> List[BookingType]:
        session: Session = info.context['request'].app.state.session

        bookings = await booking_list(session)
        return [PydanticBooking.from_orm(booking) for booking in bookings]
