from starlette.config import Config

config = Config()

EVENT_STORE_DATABASE_URL = config("EVENT_STORE_DATABASE_URL")
READ_DATABASE_URL = config("READ_DATABASE_URL")
RABBITMQ_BROKER_URL = config("RABBITMQ_BROKER_URL")
