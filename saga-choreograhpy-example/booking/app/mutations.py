import strawberry
from strawberry.types import Info

from app.mocks import BOOKING_LIST
from app.types import Booking
from uuid import uuid4


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_booking(self, name: str, info: Info) -> Booking:
        booking = Booking(
            uuid=str(uuid4()),
            name=name
        )
        BOOKING_LIST.append(booking)
        return booking
