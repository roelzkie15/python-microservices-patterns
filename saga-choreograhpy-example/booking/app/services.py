from typing import List
from strawberry.types import Info


from app.mocks import BOOKING_LIST
from app.types import Booking


async def booking_details(uuid: str) -> Booking:
    return [booking for booking in BOOKING_LIST if booking.uuid == uuid][0]

async def booking_list() -> List[Booking]:
    return BOOKING_LIST
