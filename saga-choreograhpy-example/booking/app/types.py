import strawberry


@strawberry.type
class Booking:
    id: int
    name: str
    status: str = 'created'
