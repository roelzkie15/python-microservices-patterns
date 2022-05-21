
from typing import List

import strawberry
from strawberry.types import Info

from app.object_types import BillingRequestType
from app.pydantic_models import PydanticBillingRequest
from app.services import billing_request_details, billing_request_list


@strawberry.type
class Query:

    @strawberry.field
    async def billing_request_details(self, id: int, info: Info) -> BillingRequestType:
        br = await billing_request_details(id)
        return PydanticBillingRequest.from_orm(br)

    @strawberry.field
    async def billing_request_list(self, info: Info) -> List[BillingRequestType]:
        br_list = await billing_request_list()
        return [PydanticBillingRequest.from_orm(br) for br in br_list]
