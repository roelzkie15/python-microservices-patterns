import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.amqp_client import AMQPClient
from app.models import AMQPMessage
from app.object_types import BookingType
from app.pydantic_models import PydanticBooking
from app.services import create_booking


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_booking(self, description: str, info: Info) -> BookingType:
        session: Session = info.context['request'].app.state.session

        booking = await create_booking(session, description=description)
        pydantic_booking = PydanticBooking.from_orm(booking)

        amqp_client: AMQPClient = info.context['request'].app.state.amqp_client
        await amqp_client.event_producer(
            'BOOKING_TX_EVENT_STORE', 'booking.created', message=AMQPMessage(id=str(booking.uuid), content=pydantic_booking.dict())
        )

        return pydantic_booking
