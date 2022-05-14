from uuid import uuid4

import strawberry
from strawberry.types import Info

from app.amqp_client import AMQPClient
from app.mocks import BOOKING_LIST
from app.models import AMQPMessage
from app.object_types import BookingType
from app.services import create_booking
from app.pydantic_models import PydanticBooking


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_booking(self, desc: str, info: Info) -> BookingType:
        booking = await create_booking(desc=desc)
        pydantic_booking = PydanticBooking.from_orm(booking)

        amqp_client: AMQPClient = info.context['amqp_client']
        await amqp_client.event_producer(
            'MANAGER_EVENT_STORE', 'booking.created', message=AMQPMessage(id=str(booking.uuid), content=pydantic_booking.dict())
        )

        return pydantic_booking
