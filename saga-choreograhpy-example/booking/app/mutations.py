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
    async def create_booking(self, parking_slot_uuid: str, info: Info) -> BookingType:
        session: Session = info.context['request'].app.state.session

        booking = await create_booking(session, parking_slot_uuid=parking_slot_uuid)
        pydantic_booking = PydanticBooking.from_orm(booking)

        amqp_client: AMQPClient = info.context['request'].app.state.amqp_client
        await amqp_client.event_producer(
            'BOOKING_TX_EVENT_STORE', 'booking.created', message=AMQPMessage(id=str(booking.parking_slot_uuid), content=pydantic_booking.dict())
        )

        return pydantic_booking
