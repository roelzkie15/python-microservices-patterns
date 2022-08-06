import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import settings

engine = create_engine(settings.PROJECTOR_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ProjectorBase = declarative_base()


@contextlib.contextmanager
def Session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
