import contextlib
from uuid import UUID

from eventsourcing.application import Application
from eventsourcing.dispatch import singledispatchmethod
from eventsourcing.system import (ProcessApplication, SingleThreadedRunner,
                                  System)

from app.amqp_client import AMQP, AMQPClient
from app.domainmodels import Booking
from app.models import AMQPMessage
from app.services import create_booking, update_booking_status_by


class Bookings(Application):
    def create_booking(self, parking_slot_ref_no: str) -> UUID:
        booking = Booking(parking_slot_ref_no=parking_slot_ref_no)
        self.save(booking)
        return booking.id

    def reserve_booking(self, booking_id: UUID) -> Booking:
        booking: Booking = self.get_booking(booking_id)
        self._status_checker(booking, "reserved")
        booking.reserve()
        return self._update_booking(booking)

    def complete_booking(self, booking_id: UUID) -> Booking:
        booking: Booking = self.get_booking(booking_id)
        self._status_checker(booking, "completed")
        booking.complete()
        return self._update_booking(booking)

    def get_booking(self, booking_id: UUID) -> Booking:
        booking = self.repository.get(booking_id)
        return booking

    def _status_checker(self, booking: Booking, status: str):
        if booking.status == status:
            raise ValueError(f"Booking ID: {booking.id} is already {booking.status}.")
        return booking

    def _update_booking(self, booking: Booking) -> Booking:
        self.save(booking)
        return booking


class BookingProjector(ProcessApplication):
    @singledispatchmethod
    def policy(self, domain_event, processing_event):
        if type(domain_event) is Booking.BookingCreated:
            create_booking(
                domain_uuid=str(domain_event.originator_id),
                parking_slot_ref_no=domain_event.parking_slot_ref_no,
                status=domain_event.status,
            )
        else:
            # Aside from booking created event, there only have
            # a booking status change events.
            update_booking_status_by(
                domain_uuid=str(domain_event.originator_id),
                status=domain_event.status,
            )


system = System(pipes=[[Bookings, BookingProjector]])


@contextlib.contextmanager
def process_runner():
    runner = SingleThreadedRunner(system)
    try:
        runner.start()
        yield runner
    finally:
        runner.stop()
