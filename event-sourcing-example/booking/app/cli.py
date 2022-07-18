from uuid import UUID
import fire
from booking.app.applications import Bookings


class AppCLI(object):

    def create_booking_request(self, parking_slot_ref_no: str) -> UUID:
        booking_app = Bookings()
        return booking_app.create_booking(parking_slot_ref_no=parking_slot_ref_no)


if __name__ == "__main__":
    fire.Fire(AppCLI)
