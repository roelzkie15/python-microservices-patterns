import strawberry

from app.pydantic_models import PydanticParkingSlot


@strawberry.experimental.pydantic.type(model=PydanticParkingSlot, all_fields=True)
class ParkingSlotType:
    pass
