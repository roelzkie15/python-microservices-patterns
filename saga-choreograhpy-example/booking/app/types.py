import strawberry


@strawberry.type
class Booking:
    uuid: str
    name: str
    status: str = 'created'
