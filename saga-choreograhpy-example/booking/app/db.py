import fire
from sqlmodel import SQLModel, create_engine

# This is needed
# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#sqlmodel-metadata-order-matters
from app import models
from app.dependencies import get_settings


settings = get_settings()
engine = create_engine(settings.DB_URL, echo=True)
