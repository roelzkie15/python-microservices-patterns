from functools import partial
from typing import Callable

import aio_pika
from fastapi import FastAPI

from app.services import update_booking_status_from_event


async def init_consumer(app: FastAPI) -> None:
    # Creating channel
    channel = await app.state.amqp_connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare exchange
    exchange = await channel.declare_exchange(
        'BOOKING_SERVICE_EXCHANGE',
        type='topic',
        durable=True
    )

    await handle_incoming_booking_service_events(channel, exchange)


async def handle_incoming_booking_service_events(channel: aio_pika.Channel, exchange: aio_pika.exchange.Exchange) -> None:
    # Declaring queue
    invoice_event_queue = await channel.declare_queue('INVOICE_EVENT_QUEUE', auto_delete=True)
    await watch_from_invoice_event(
        exchange, invoice_event_queue, 'INVOICE_GENERATED_EVENT',
        update_booking_status_from_event
    )


async def watch_from_invoice_event(exchange: aio_pika.exchange.Exchange, queue: aio_pika.queue.Queue, event_name: str, callback: Callable) -> None:
    await queue.bind(exchange, event_name)
    await queue.consume(partial(process_message, callback=callback))


async def process_message(message: aio_pika.abc.AbstractIncomingMessage, callback: Callable) -> None:
    async with message.process(ignore_processed=True):
        await message.ack()
        await callback(message.body)
