from starlette.config import Config

config = Config()

DATABASE_URL = config('DATABASE_URL')
RABBITMQ_BROKER_URL = config('RABBITMQ_BROKER_URL')
