from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str
    DB_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
