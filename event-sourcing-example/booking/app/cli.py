from uuid import UUID

import fire

from app.applications import Bookings, process_runner


class AppCLI(object):
    def create_booking_request(self, parking_slot_ref_no: str) -> UUID:
        with process_runner() as runner:
            booking_app = runner.get(Bookings)
            result_id = booking_app.create_booking(
                parking_slot_ref_no=parking_slot_ref_no
            )
        return result_id

    def reserve_booking(self, booking_id: str) -> UUID:
        with process_runner() as runner:
            booking_app = runner.get(Bookings)
            booking = booking_app.reserve_booking(booking_id=booking_id)
            return booking.id

    def complete_booking(self, booking_id: str) -> UUID:
        with process_runner() as runner:
            booking_app = runner.get(Bookings)
            booking = booking_app.complete_booking(booking_id=booking_id)
            return booking.id


if __name__ == "__main__":
    fire.Fire(AppCLI)
