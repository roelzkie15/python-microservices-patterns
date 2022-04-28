import strawberry


@strawberry.type
class BookingType:
    uuid: str
    name: str
    status: str = 'created'
