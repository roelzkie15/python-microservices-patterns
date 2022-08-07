from app.db import Session
from app.models import Booking


def create_booking(domain_uuid: str, parking_slot_ref_no: str, status: str) -> Booking:
    with Session() as session:
        booking = Booking(
            domain_uuid=domain_uuid,
            parking_slot_ref_no=parking_slot_ref_no,
            status=status,
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking


def get_booking_by_domain_uuid(domain_uuid: str) -> Booking:
    with Session() as session:
        return session.query(Booking).filter(Booking.domain_uuid == domain_uuid).one()


def update_booking_status_by(domain_uuid: str, status: str) -> Booking:
    with Session() as session:
        booking = get_booking_by_domain_uuid(domain_uuid)
        booking.status = status
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking
