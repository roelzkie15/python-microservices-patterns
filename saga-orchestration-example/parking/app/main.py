import ast
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
from app.services import block_parking_slot


async def reply_producer(
    reply_to: str, correlation_id: str, data: str
):

    connection = await aio_pika.connect_robust(
        settings.RABBITMQ_BROKER_URL, loop=asyncio.get_event_loop()
    )

    channel = await connection.channel()

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


async def parking_command_event_processor(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        command = message.headers.get('COMMAND')
        client = message.headers.get('CLIENT')

        response_obj: CommandResponse = None
        if client == 'BOOKING_REQUEST_ORCHESTRATOR' and command == 'PARKING_RESERVE':
            with Session() as session:
                booking = ast.literal_eval(message.body.decode('utf-8'))
                parking_slot_uuid = booking.get('parking_slot_ref_no').split(':')[0]
                is_blocked = await block_parking_slot(session, parking_slot_uuid)

                await message.ack()

                if is_blocked:
                    response_obj = CommandResponse(
                        content=None,
                        reply_state='PARKING_AVAILABLE'
                    )

        # There must be a response object to signal orchestrator of
        # the outcome of the request.
        assert response_obj is not None

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
        await queue.bind(exchange, 'parking.*')
        await queue.consume(parking_command_event_processor)

        yield
    finally:
        await connection.close()


async def root(request):
    return JSONResponse({'message': 'Parking server is running'})

routes = [
    Route('/', root),
]

app = Starlette(routes=routes, lifespan=lifespan)
