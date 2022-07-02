from aio_pika import DeliveryMode, Message, connect
from app import logging, settings


async def replicate_parking_slot(ps) -> None:
    # Perform connection
    connection = await connect(settings.RABBITMQ_BROKER_URL)

    async with connection:
        # Creating a channel
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "CQRS_EVENT_STORE", type="topic", durable=True
        )

        message_body = str(ps).encode()

        message = Message(
            message_body,
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        # Sending the message
        await exchange.publish(message, routing_key="parking.create")

        logging.info(f"Sent message: {message!r}")
