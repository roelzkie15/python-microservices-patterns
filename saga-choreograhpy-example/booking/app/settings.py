from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    RABBITMQ_BROKER_URL: str
