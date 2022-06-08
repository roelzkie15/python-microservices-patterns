import asyncio
import contextlib

import aio_pika
from aio_pika import IncomingMessage, Message
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app import settings


async def reply_producer(
    channel: str, correlation_id: str, data: str
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
        routing_key=channel,
    )

    await connection.close()


async def process_consumer(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        await message.ack()
        print('so: messsage acknowledge in parking service')
        print(message)
        print(message.body)

        # Bugy, unable to produce message.
        await reply_producer(
            message.reply_to, message.correlation_id, message.body.decode('utf-8')
        )


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

        queue = await channel.declare_queue(auto_delete=True)
        await queue.bind(exchange, 'parking.*')
        await queue.consume(process_consumer)

        yield
    finally:
        await connection.close()


async def root(request):
    return JSONResponse({'message': 'Parking server is running'})

routes = [
    Route('/', root),
]

app = Starlette(routes=routes, lifespan=lifespan)
