from uuid import UUID

import fire

from app.applications import Bookings, process_runner
from app.services import get_booking_by_domain_uuid, get_booking_list


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

    def get_booking_details(self, booking_id: str):
        booking = get_booking_by_domain_uuid(booking_id)
        return booking.to_dict()

    def get_booking_list(self):
        booking_list = get_booking_list()
        return [booking.to_dict() for booking in booking_list]

    def get_booking_events(self, booking_id: str):
        booking_app = Bookings()
        events = booking_app.get_booking_history(booking_id)
        return events


if __name__ == "__main__":
    fire.Fire(AppCLI)
