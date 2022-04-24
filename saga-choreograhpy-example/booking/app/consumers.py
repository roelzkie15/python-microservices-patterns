from functools import partial
from typing import Callable

import aio_pika
from fastapi import FastAPI

from app.services import update_booking_status_from_event


async def init_consumers(app: FastAPI) -> None:
    '''
    Initialize event consumers for Booking Service. Consumers will watch incoming messages
    from an exchange (e.g. BOOKING_SERVICE_EXCHANGE).

    An Exchange may have multiple queues and each queue represent a service event-store (e.g. INVOICE_EVENT_STORE).

    A Queue can store messages/events produced by a service. A service may produce multiple events
    (e.g. invoice.generated.success) this will represent our Binding Key.

    Binding Key will help deliver messages/events produced by a service to the right event-store.
    '''

    # Creating channel
    channel = await app.state.amqp_connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declare exchange
    exchange = await channel.declare_exchange(
        'BOOKING_SERVICE_EXCHANGE',
        type='topic',
        durable=True
    )

    # WIP: more queues to come.
    # === Declaring queues === 

    # A queue where invoice service publish its events/messages.
    invoice_event_store = await channel.declare_queue('INVOICE_EVENT_STORE', auto_delete=True)
    
    # === Invoice consumers ===

    # Consume events/messages from invoice event store.
    await event_consumer(
        exchange, invoice_event_store,
        update_booking_status_from_event,
        'invoice.generated.success'
    )


async def event_consumer(
    exchange: aio_pika.exchange.Exchange, queue: aio_pika.queue.Queue, callback: Callable, binding_key: str = '#', 
) -> None:
    '''
    A function that will consume messages from a specific event-store (Queue).
    You can specify a `binding_key` to consume specific set of events otherwise
    it will consume any messages from the given event-store.
    '''
    await queue.bind(exchange, binding_key)
    await queue.consume(partial(process_message, callback=callback))


async def process_message(message: aio_pika.IncomingMessage, callback: Callable) -> None:
    '''
    Process incoming message from a Queue. It will require a callback function to handle
    message content.
    '''
    async with message.process(ignore_processed=True):
        await message.ack()
        await callback(message.body)
