from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    RABBITMQ_BROKER_URL: str
