import strawberry
from strawberry.types import Info

from app.object_types import ParkingCreateInput, ParkingSlotType
from app.pydantic_models import PydanticParkingSlot
from app.services import create_parking_slot


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_parking_slot(self, input: ParkingCreateInput, info: Info) -> ParkingSlotType:
        session = info.context['request'].app.state.session
        ps = await create_parking_slot(session, **input.__dict__)
        return PydanticParkingSlot.from_orm(ps)

