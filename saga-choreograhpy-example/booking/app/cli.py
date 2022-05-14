
import fire

from app.db import Base, engine
from app.services import create_booking


class BookingAppEngine:

    def create_all_tables(self):
        Base.metadata.create_all(engine)

    def drop_all_tables(self):
        Base.metadata.drop_all(engine)

    async def create_booking(self, desc: str):
        booking = await create_booking(desc=desc)
        print(f'New booking was created: {booking.uuid}')


if __name__ == '__main__':
    fire.Fire(BookingAppEngine)
