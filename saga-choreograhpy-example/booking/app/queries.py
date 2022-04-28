
from typing import List
from strawberry.types import Info
import strawberry

from app.services import booking_details, booking_list
from app.types import BookingType


@strawberry.type
class Query:
    @strawberry.field
    def booking(self, uuid: str, info: Info) -> BookingType:
        return booking_details(uuid)

    @strawberry.field
    def bookings(info: Info) -> List[BookingType]:
        return booking_list()
