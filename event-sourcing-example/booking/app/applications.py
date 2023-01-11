import contextlib
from typing import List
from uuid import UUID

from app.amqp_client import AMQP, AMQPClient
from app.domainmodels import Booking
from app.models import AMQPMessage
from app.services import create_booking, update_booking_status_by
from attrs import asdict
from eventsourcing.application import Application
from eventsourcing.dispatch import singledispatchmethod
from eventsourcing.system import ProcessApplication, SingleThreadedRunner, System

BOOKING_EVENT_ATTRIBUTES = ['originator_id', 'status', 'parking_slot_ref_no', 'originator_version']
BOOKING_EVENT_ATTRIBUTES_MAPPER = {'originator_id': 'id', 'originator_version': 'version'}


class Bookings(Application):
    def create_booking(self, parking_slot_ref_no: str) -> UUID:
        booking = Booking(parking_slot_ref_no=parking_slot_ref_no)
        self.save(booking)
        return booking.id

    def reserve_booking(self, booking_id: str) -> Booking:
        booking: Booking = self.get_booking(booking_id)
        self._status_checker(booking, "reserved")
        booking.reserve()
        return self._update_booking(booking)

    def complete_booking(self, booking_id: str) -> Booking:
        booking: Booking = self.get_booking(booking_id)
        self._status_checker(booking, "completed")
        booking.complete()
        return self._update_booking(booking)

    def get_booking(self, booking_id: str) -> Booking:
        booking = self.repository.get(booking_id)
        return booking

    def get_booking_history(self, booking_id: str) -> List[dict] | List:
        booking_events = list(self.events.get(booking_id))
        booking_event_dicts = []

        for booking_event in booking_events:
            booking_event_dict = booking_event.__dict__

            event_dict = {
                BOOKING_EVENT_ATTRIBUTES_MAPPER.get(event_key, event_key): booking_event_dict.get(event_key)
                for event_key in sorted(booking_event_dict.keys())
                if event_key in BOOKING_EVENT_ATTRIBUTES
            }
            booking_event_dicts.append(event_dict)

        return booking_event_dicts

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
            booking = create_booking(
                domain_uuid=str(domain_event.originator_id),
                parking_slot_ref_no=domain_event.parking_slot_ref_no,
                status=domain_event.status,
            )

            with AMQP() as amqp:
                amqp_client: AMQPClient = amqp
                amqp_client.event_producer(
                    "BOOKING_TX_EVENT",
                    "booking.create",
                    AMQPMessage(
                        id=booking.parking_slot_ref_no, content=booking.to_dict()
                    ),
                )

        else:
            # Aside from booking created event, there is only have
            # a booking status change events.
            booking = update_booking_status_by(
                domain_uuid=str(domain_event.originator_id),
                status=domain_event.status,
            )
            with AMQP() as amqp:
                amqp_client: AMQPClient = amqp
                amqp_client.event_producer(
                    "BOOKING_TX_EVENT",
                    "booking.status_changed",
                    AMQPMessage(
                        id=booking.parking_slot_ref_no, content=booking.to_dict()
                    ),
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
