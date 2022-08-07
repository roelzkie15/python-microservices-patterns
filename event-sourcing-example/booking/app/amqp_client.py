import contextlib
import json

import attrs
import pika

from app import settings
from app.models import AMQPMessage


class AMQPClient:

    def init(self):
        '''
        Inititalize AMQP client.
        '''

        parameters = pika.URLParameters(settings.RABBITMQ_BROKER_URL)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        return self

    def event_producer(
        self,
        event_store: str,
        binding_key: str,
        message: AMQPMessage
    ) -> None:
        '''
        Send event/message to a specific exchange with binding-key.

        If an existing queue is bound to the given binding-key, the message will be stored
        to that queue otherwise the message will be lost.

        NOTE: The binding_key is mandatory so we can explicitly route the message/event
            to the right queue.
        '''

        # Declare exchange
        self.channel.exchange_declare(
            exchange=event_store,
            exchange_type='topic',
            durable=True
        )

        payload = json.dumps(attrs.asdict(message))
        self.channel.basic_publish(
            exchange=event_store, routing_key=binding_key, body=payload
        )


@contextlib.contextmanager
def AMQP() -> AMQPClient:
    client = AMQPClient().init()
    try:
        yield client
    finally:
        client.connection.close()
