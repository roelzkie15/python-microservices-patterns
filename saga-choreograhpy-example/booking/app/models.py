from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Booking(SQLModel, table=True):
    uuid: UUID = Field(default=uuid4(), primary_key=True)
    name: str
    status: str
