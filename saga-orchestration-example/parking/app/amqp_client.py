import asyncio
from functools import partial
from typing import Callable

import aio_pika
import simplejson as json
from aio_pika import IncomingMessage, Message

from app import settings
from app.models import AMQPMessage


class AMQPClient:

    async def init(self) -> None:
        '''
        Inititalize AMQP client.
        '''

        self.connection = await aio_pika.connect_robust(
            settings.RABBITMQ_BROKER_URL, loop=asyncio.get_event_loop()
        )

        # Creating channel
        self.channel = await self.connection.channel()
        return self

    async def event_consumer(
        self, callback: Callable, event_store: str, event: str = '#', queue_name: str | None = None,
    ) -> None:
        '''
        Create an event consumer.

        callback    -   A function that will process the incoming message.
        event_store -   Declare an exchange as an event store. We store send messages/events
                        to this exchange.
        event       -   Serves as a binding key or a type of event that occurred.
        queue_name  -   Create a queue to set of events from the Exchange (Optional).
                        If not specified it will still create a queue with a random name.
        '''
        exchange = await self.channel.declare_exchange(
            event_store,
            type='topic',
            durable=True
        )
        queue = await self.channel.declare_queue(queue_name, auto_delete=True)

        await queue.bind(exchange, event)
        await queue.consume(partial(self._process_message, callback=callback))

    async def event_producer(
        self, event_store: str, binding_key: str, correlation_id: str, message: AMQPMessage
    ) -> None:
        '''
        Send event/message to a specific exchange with binding-key.

        If an existing queue is bound to the given binding-key, the message will be stored
        to that queue otherwise the message will be lost.

        NOTE: The binding_key is mandatory so we can explicitly route the message/event
            to the right queue.
        '''

        # Declare exchange
        exchange = await self.channel.declare_exchange(
            event_store,
            type='topic',
            durable=True
        )

        payload = json.dumps(message.dict())
        await exchange.publish(
            Message(
                body=str(payload).encode(),
                content_type='application/json',
                correlation_id=correlation_id
            ),
            routing_key=binding_key,
        )

    async def _process_message(self, message: IncomingMessage, callback: Callable) -> None:
        '''
        Process incoming message from a Queue. It will require a callback function to handle
        message content.
        '''
        async with message.process(ignore_processed=True):
            await callback(message)
