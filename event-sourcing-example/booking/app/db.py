import contextlib

from app import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

engines = {
    "primary": create_engine(settings.DATABASE_URL, logging_name="primary"),
    "replica": create_engine(settings.REPLICA_DATABASE_URL, logging_name="replica"),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None):
        if mapper and mapper.class_.__name__ == "BookingReplica":
            return engines["replica"]
        elif self._flushing:
            return engines["primary"]
        else:
            return engines["replica"]


SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, class_=RoutingSession)
)

Base = declarative_base()
ReplicaBase = declarative_base()


@contextlib.contextmanager
def Session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
