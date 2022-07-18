import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app import settings

engines = {
    "event_store": create_engine(settings.EVENT_STORE_DATABASE_URL, logging_name="event_store"),
    "read_db": create_engine(settings.READ_DATABASE_URL, logging_name="read_db"),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None):
        # if mapper and mapper.class_.__name__ == "BookingReplica":
        #     return engines["read_db"]
        if self._flushing:
            return engines["event_store"]
        else:
            return engines["read_db"]


SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, class_=RoutingSession)
)

EventStoreBase = declarative_base()
ReadDBBase = declarative_base()


@contextlib.contextmanager
def Session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
