from aio_pika import Message


async def event_producer(
    app, exchange: str, message, binding_key: str
) -> None:
    '''
    Send event/message to a specific exchange and binding-key.
    
    If an existing queue is bound to the given binding-key, the message will be stored
    to that event-store (Queue) otherwise the message will be lost.
    '''
    conn = app.state.amqp_connection
    # Creating channel
    channel = await conn.channel()

    # Declare exchange
    exchange = await channel.declare_exchange(
        exchange,
        type='topic',
        durable=True
    )

    await exchange.publish(
        Message(
            body=message.encode(),
            content_type="application/json",
        ),
        routing_key=binding_key,
    )
