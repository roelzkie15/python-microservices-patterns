import strawberry
from strawberry.types import Info

from app.mocks import LIST_OF_BOOKINGS
from app.types import Booking


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_booking(self, name: str, info: Info) -> Booking:
        booking = Booking(
            id=len(LIST_OF_BOOKINGS) + 1,
            name=name
        )
        LIST_OF_BOOKINGS.append(booking)
        return booking
