from pyexpat import model
import strawberry
from app.models import Booking


@strawberry.experimental.pydantic.type(model=Booking, all_fields=True)
class BookingType:
    pass
