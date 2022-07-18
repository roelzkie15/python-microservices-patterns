from uuid import UUID

from booking.app.domainmodels import Booking
from eventsourcing.application import Application


class Bookings(Application):

    def create_booking(self, parking_slot_ref_no: str) -> UUID:
        booking = Booking(parking_slot_ref_no=parking_slot_ref_no)
        self.save(booking)
        return booking.id

    def reserve_booking(self, booking_id: UUID) -> Booking:
        booking: Booking = self.get_booking(booking_id)
        booking.reserve()
        return self._update_booking(booking)

    def complete_booking(self, booking_id: UUID) -> Booking:
        booking: Booking = self.get_booking(booking_id)
        booking.complete()
        return self._update_booking(booking)

    def get_booking(self, booking_id: UUID) -> Booking:
        booking = self.repository.get(booking_id)
        return booking

    def _update_booking(self, booking: Booking) -> Booking:
        self.save(booking)
        return booking
