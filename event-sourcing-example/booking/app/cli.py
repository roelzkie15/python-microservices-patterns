from uuid import UUID

import fire
from app.applications import Bookings


class AppCLI(object):
    def create_booking_request(self, parking_slot_ref_no: str) -> UUID:
        booking_app = Bookings()
        return booking_app.create_booking(parking_slot_ref_no=parking_slot_ref_no)

    def reserve_booking(self, booking_id: str) -> UUID:
        booking_app = Bookings()
        booking = booking_app.reserve_booking(booking_id=booking_id)
        return booking.id

    def complete_booking(self, booking_id: str) -> UUID:
        booking_app = Bookings()
        booking = booking_app.complete_booking(booking_id=booking_id)
        return booking.id


if __name__ == "__main__":
    fire.Fire(AppCLI)
