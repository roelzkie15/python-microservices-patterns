from eventsourcing.domain import Aggregate, event


class Booking(Aggregate):
    @event("BookingCreated")
    def __init__(self, parking_slot_ref_no: str, status: str = "created") -> None:
        self.parking_slot_ref_no = parking_slot_ref_no
        self.status = status

    @event("BookingReserved")
    def reserve(self, status: str = "reserved"):
        self.status = status

    @event("BookingCompleted")
    def complete(self, status: str = "completed"):
        self.status = status
