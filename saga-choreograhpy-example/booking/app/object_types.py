import strawberry

from app.pydantic_models import PydanticBooking


@strawberry.experimental.pydantic.type(model=PydanticBooking, all_fields=True)
class BookingType:
    pass
