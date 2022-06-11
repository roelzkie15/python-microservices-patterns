import asyncio
import contextlib

import aio_pika
from aio_pika import IncomingMessage, Message
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app import settings
from app.db import Session
from app.models import CommandResponse


async def reply_producer(
    reply_to: str, correlation_id: str, data: str
):

    connection = await aio_pika.connect_robust(
        settings.RABBITMQ_BROKER_URL, loop=asyncio.get_event_loop()
    )

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare exchange
    exchange = await channel.declare_exchange(
        'BOOKING_TX_EVENT_STORE',
        type='topic',
        durable=True
    )

    await exchange.publish(
        Message(
            body=data.encode(),
            content_type='application/json',
            correlation_id=correlation_id
        ),
        routing_key=reply_to,
    )

    await connection.close()


async def billing_command_event_processor(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        command = message.headers('COMMAND', None)
        response_obj = {}

        await reply_producer(message.reply_to, message.correlation_id, str(response_obj.dict()))


@contextlib.asynccontextmanager
async def lifespan(app):
    connection = await aio_pika.connect_robust(
        settings.RABBITMQ_BROKER_URL, loop=asyncio.get_event_loop()
    )

    try:
        # Creating channel
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            'BOOKING_TX_EVENT_STORE',
            type='topic',
            durable=True
        )

        # Parking command channel.
        queue = await channel.declare_queue(auto_delete=True)
        await queue.bind(exchange, 'billing.*')
        await queue.consume(billing_command_event_processor)

        yield
    finally:
        await connection.close()


async def root(request):
    return JSONResponse({'message': 'Billing server is running'})

routes = [
    Route('/', root),
]

app = Starlette(routes=routes, lifespan=lifespan)
