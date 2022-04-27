from uuid import uuid4

import strawberry
from strawberry.types import Info

from app.amqp_client import AMQPClient
from app.mocks import BOOKING_LIST
from app.models import AMQPMessage
from app.types import Booking


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_booking(self, name: str, info: Info) -> Booking:
        booking = Booking(
            uuid=str(uuid4()),
            name=name
        )
        BOOKING_LIST.append(booking)

        amqp_client: AMQPClient = info.context['amqp_client']
        await amqp_client.event_producer(
            'MANAGER_EVENT_STORE', 'booking.created', message=AMQPMessage(id=booking.uuid, body=booking)
        )

        return booking
