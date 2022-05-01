from uuid import uuid4

import strawberry
from strawberry.types import Info

from app.amqp_client import AMQPClient
from app.mocks import BOOKING_LIST
from app.models import AMQPMessage
from app.object_types import BookingType
from app.services import create_booking


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_booking(self, desc: str, info: Info) -> BookingType:
        booking = await create_booking(desc=desc)

        amqp_client: AMQPClient = info.context['amqp_client']
        await amqp_client.event_producer(
            'MANAGER_EVENT_STORE', 'booking.created', message=AMQPMessage(id=str(booking.uuid), content=booking)
        )

        return booking
