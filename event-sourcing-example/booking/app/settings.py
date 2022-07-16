from starlette.config import Config

config = Config()

DATABASE_URL = config("DATABASE_URL")
REPLICA_DATABASE_URL = config("REPLICA_DATABASE_URL")
RABBITMQ_BROKER_URL = config("RABBITMQ_BROKER_URL")
