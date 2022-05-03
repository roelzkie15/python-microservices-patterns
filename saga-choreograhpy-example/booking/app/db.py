import fire
from sqlmodel import create_engine

from app.dependencies import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, echo=True)
