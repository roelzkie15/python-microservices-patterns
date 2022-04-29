from typing import List

from strawberry.types import Info

from app.mocks import BOOKING_LIST
from app.object_types import BookingType


async def booking_details(uuid: str) -> BookingType:
    return [booking for booking in BOOKING_LIST if booking.uuid == uuid][0]


async def booking_list() -> List[BookingType]:
    return BOOKING_LIST


async def test_consume(message_body: bytes) -> None:
    print('test consume: ', message_body.decode())
