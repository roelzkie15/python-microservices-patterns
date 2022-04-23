from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str
    DB_PASSWORD: str

    RABBITMQ_BROKER_URL: str
