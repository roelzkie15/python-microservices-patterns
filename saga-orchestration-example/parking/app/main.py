import ast
import asyncio
import contextlib

import aio_pika
from aio_pika import IncomingMessage, Message
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.services import parking_command_event_processor
from app.amqp_client import AMQPClient


@contextlib.asynccontextmanager
async def lifespan(app):
    amqp_client: AMQPClient = await AMQPClient().init()

    try:
        await amqp_client.event_consumer(parking_command_event_processor, 'BOOKING_TX_EVENT_STORE', 'parking.*')
        yield
    finally:
        await amqp_client.connection.close()


async def health(request):
    return JSONResponse({'message': 'Parking server is running'})

routes = [
    Route('/health', health),
]

app = Starlette(routes=routes, lifespan=lifespan)
