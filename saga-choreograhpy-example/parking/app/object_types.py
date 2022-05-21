import strawberry

from app.pydantic_models import PydanticBookingRequest


@strawberry.experimental.pydantic.type(model=PydanticBookingRequest, all_fields=True)
class BookingRequestType:
    pass

@strawberry.type
class AlreadyApprovedError:
    message: str = 'Unprocessable Entity'
    status_code: int = 422

# Create a Union type to represent the 2 results from the mutation
ApproveActionResponse = strawberry.union(
    'ApproveActionResponse', [BookingRequestType, AlreadyApprovedError]
)
