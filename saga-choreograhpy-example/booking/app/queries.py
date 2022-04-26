
from typing import List

import strawberry

from app.services import booking_details, booking_list
from app.types import Booking


@strawberry.type
class Query:
    booking: Booking = strawberry.field(resolver=booking_details)
    bookings: List[Booking] = strawberry.field(resolver=booking_list)
