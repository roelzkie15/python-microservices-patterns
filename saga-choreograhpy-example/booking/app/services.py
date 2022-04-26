from typing import List

from app.mocks import LIST_OF_BOOKINGS
from app.types import Booking


async def booking_details(id: int) -> Booking:
    return [booking for booking in LIST_OF_BOOKINGS if booking.id == id][0]

async def booking_list() -> List[Booking]:
    return LIST_OF_BOOKINGS
