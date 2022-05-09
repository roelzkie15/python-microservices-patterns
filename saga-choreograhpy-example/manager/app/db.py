from sqlalchemy import MetaData
from sqlmodel import SQLModel, create_engine

from app.dependencies import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, echo=True)

SQLModel.metadata = MetaData(schema='manager_schema')
