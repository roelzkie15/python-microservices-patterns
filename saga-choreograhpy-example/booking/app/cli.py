
import fire
from sqlmodel import SQLModel

# This is needed
# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#sqlmodel-metadata-order-matters
from app import models

from app.db import engine
from app.services import create_booking


class BookingAppEngine:

    def create_all_tables(self):
        SQLModel.metadata.create_all(engine)

    def drop_all_tables(self):
        SQLModel.metadata.drop_all(engine)

    async def create_booking(self, desc: str):
        booking = await create_booking(desc=desc)
        print(f'New booking was created: {booking.uuid}')


if __name__ == '__main__':
    fire.Fire(BookingAppEngine)
