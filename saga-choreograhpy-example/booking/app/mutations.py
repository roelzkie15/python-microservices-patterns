from uuid import uuid4

import strawberry
from strawberry.types import Info

from app.amqp_client import AMQPClient
from app.mocks import BOOKING_LIST
from app.models import AMQPMessage, Booking
from app.object_types import BookingType


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_booking(self, desc: str, info: Info) -> BookingType:
        booking = Booking(
            uuid=str(uuid4()),
            desc=desc
        )
        BOOKING_LIST.append(booking)

        amqp_client: AMQPClient = info.context['amqp_client']
        await amqp_client.event_producer(
            'MANAGER_EVENT_STORE', 'booking.created', message=AMQPMessage(id=booking.uuid, body=booking)
        )

        return booking
