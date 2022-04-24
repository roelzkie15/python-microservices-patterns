from aio_pika import Message


async def event_producers(app, event: str, queue_name, message) -> None:
    conn = app.state.amqp_connection
    # Creating channel
    channel = await conn.channel()

    # Declare exchange
    exchange = await channel.declare_exchange(
        'BOOKING_SERVICE_EXCHANGE',
        type='topic',
        durable=True
    )

    queue = await channel.declare_queue(queue_name, auto_delete=True)
    await queue.bind(exchange, event)

    await exchange.publish(
        Message(
            body=message.encode(),
            content_type="application/json",
            headers={"foo": "bar"},
        ),
        routing_key=event,
    )
