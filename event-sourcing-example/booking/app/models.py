from typing import Dict


class DictMixin:
    def to_dict(self) -> Dict:
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


# class Booking(DictMixin, Base):
#     __tablename__ = "bookings"

#     id = Column(Integer, primary_key=True, unique=True, index=True)
#     status = Column(String, nullable=False, server_default="created")

#     parking_slot_ref_no = Column(String, nullable=True)


# class BookingReplica(DictMixin, ReplicaBase):
#     __tablename__ = "bookings"

#     id = Column(Integer, primary_key=True, unique=True, index=True)
#     status = Column(String, nullable=False, server_default="created")

#     parking_slot_ref_no = Column(String, nullable=True)
