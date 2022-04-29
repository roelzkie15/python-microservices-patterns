
from typing import List

import strawberry
from strawberry.types import Info

from app.object_types import BookingType
from app.services import booking_details, booking_list


@strawberry.type
class Query:
    @strawberry.field
    def booking(self, uuid: str, info: Info) -> BookingType:
        return booking_details(uuid)

    @strawberry.field
    def bookings(info: Info) -> List[BookingType]:
        return booking_list()
