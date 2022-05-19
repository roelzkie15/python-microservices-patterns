import strawberry
from strawberry.types import Info

from app.amqp_client import AMQPClient, AMQPMessage
from app.object_types import AlreadyApprovedError, ApproveActionResponse
from app.pydantic_models import PydanticBookingRequest
from app.services import approve_booking_request, booking_request_details


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def approve_booking_request(self, uuid: str, info: Info) -> ApproveActionResponse:
        booking_request = await booking_request_details(uuid)
        if booking_request.approved:
            return AlreadyApprovedError(message=f'Booking request with ID {uuid} is already approved.')

        approved_booking_request = await approve_booking_request(booking_request)
        context = PydanticBookingRequest.from_orm(approved_booking_request)

        # amqp_client: AMQPClient = info.context['amqp_client']
        # await amqp_client.event_producer(
        #     'BILLING_EVENT_STORE', 'booking.approved', message=AMQPMessage(id=str(uuid), content=context.dict())
        # )

        return context
