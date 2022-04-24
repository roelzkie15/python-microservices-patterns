import asyncio

import aio_pika
from fastapi import FastAPI

from app.dependencies import get_settings


async def init_pika_client(app: FastAPI) -> aio_pika.Connection:
    settings = get_settings()
    app.state.amqp_connection = await aio_pika.connect_robust(
        settings.RABBITMQ_BROKER_URL, loop=asyncio.get_event_loop()
    )
