
from typing import List

import strawberry
from strawberry.types import Info

from app.object_types import BookingType
from app.pydantic_models import PydanticBooking
from app.services import booking_details, booking_list


@strawberry.type
class Query:
    @strawberry.field
    async def booking(self, uuid: str, info: Info) -> BookingType:
        booking = await booking_details(uuid)
        return PydanticBooking.from_orm(booking)

    @strawberry.field
    async def bookings(self, info: Info) -> List[BookingType]:
        bookings = await booking_list()
        return [PydanticBooking.from_orm(booking) for booking in bookings]
