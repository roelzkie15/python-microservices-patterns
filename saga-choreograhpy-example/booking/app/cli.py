
import fire
from sqlmodel import SQLModel

from app.db import engine, models
from app.services import create_booking


class BookingAppEngine:

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(engine)

    def drop_all_tables(self):
        SQLModel.metadata.drop_all(engine)

    async def create_booking(self, name: str):
        booking = await create_booking(name=name)
        print(f'New booking was created: {booking.uuid}')


if __name__ == '__main__':
    fire.Fire(BookingAppEngine)
