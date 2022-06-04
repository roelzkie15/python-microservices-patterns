
import fire

from app.db import Session
from app.services import (booking_details_by_parking_ref_no, booking_list,
                          create_booking)


class AppCLI(object):

    async def create_booking(self, parking_slot_uuid):
        with Session() as session:
            booking = await create_booking(session, parking_slot_uuid)
            return booking.to_dict()

    async def booking_list(self):
        with Session() as session:
            b_list = await booking_list(session)
            return [
                booking.to_dict() for booking in b_list
            ]

    async def booking_details_by_parking_ref_no(self, uuid: str):
        with Session() as session:
            booking = await booking_details_by_parking_ref_no(session, uuid)
            return booking.to_dict()


if __name__ == '__main__':
  fire.Fire(AppCLI)
