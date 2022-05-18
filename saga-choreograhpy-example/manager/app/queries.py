
from typing import List

import strawberry
from strawberry.types import Info

from app.object_types import BookingRequestType
from app.pydantic_models import PydanticBookingRequest
from app.services import booking_request_details, booking_request_list


@strawberry.type
class Query:
    @strawberry.field
    async def booking_request_details(self, uuid: str, info: Info) -> BookingRequestType:
        booking_request = await booking_request_details(uuid)
        return PydanticBookingRequest.from_orm(booking_request)

    @strawberry.field
    async def booking_request_list(self, info: Info) -> List[BookingRequestType]:
        br_list = await booking_request_list()
        return [PydanticBookingRequest.from_orm(br) for br in br_list]
