
from typing import List

import strawberry
from strawberry.types import Info

from app.object_types import ParkingSlotType
from app.pydantic_models import PydanticParkingSlot
from app.services import parking_slot_details, parking_slot_list


@strawberry.type
class Query:

    @strawberry.field
    async def parking_slot_list(self, info: Info) -> List[ParkingSlotType]:
        session = info.context['request'].app.state.session

        ps_list = await parking_slot_list(session)
        return [PydanticParkingSlot.from_orm(ps) for ps in ps_list]

    @strawberry.field
    async def parking_slot_details(self, uuid: str, info: Info) -> ParkingSlotType:
        session = info.context['request'].app.state.session

        ps = await parking_slot_details(session, uuid)
        print(ps)

        return PydanticParkingSlot.from_orm(ps)
