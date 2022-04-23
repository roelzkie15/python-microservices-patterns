import asyncio
import queue

import aio_pika

from app.message_handlers import set_booking_status
from app.pika_client import init_pika_client


async def init_consumer() -> None:
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(event_consumers(loop))


async def event_consumers(loop):
    conn = await init_pika_client(loop)
    async with conn:
        # Creating channel
        channel = await conn.channel()

        # Declare exchange
        exchange = await channel.declare_exchange(
            'BOOKING_SERVICE_EXCHANGE',
            type='topic'
        )

        await handle_incoming_booking_service_events(channel, exchange)


async def handle_incoming_booking_service_events(channel: aio_pika.Channel, exchange) -> None:
    # Declaring queue
    invoice_event_queue = await channel.declare_queue('INVOICE_EVENT_QUEUE', auto_delete=True)
    await watch_from_invoice_event(exchange, invoice_event_queue, 'INVOICE_GENERATED_EVENT', set_booking_status)


async def watch_from_invoice_event(exchange, queue, event_name: str, callback) -> None:
    await queue.bind(exchange, routing_key=event_name)
    await queue.consume(callback)

