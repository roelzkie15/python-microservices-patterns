
import fire

from app.db import Session
from app.models import Booking
from app.services import (booking_details_by_parking_ref_no, booking_list,
                          create_booking)
from app.sagas import CreateBookingRequestSaga


class AppCLI(object):

    async def create_booking(self, parking_slot_uuid):
            saga: CreateBookingRequestSaga = CreateBookingRequestSaga(
                parking_slot_uuid=parking_slot_uuid
            )

            async with saga.connect() as saga:
                await saga.start_workflow()

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
