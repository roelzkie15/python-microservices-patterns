import ast
import asyncio
import json

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
from app import logging, settings
from app.db import Session
from app.services import create_parking_slot_replica


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        message.ack()
        logging.info(f"message received: {message.body!r}")

        raw_ps = ast.literal_eval(message.body.decode())

        with Session() as session:
            ps = await create_parking_slot_replica(session, **raw_ps)
            logging.info(f"Replicated parking slot data: {ps.to_dict()!r}")


async def main() -> None:
    # Perform connection
    connection = await connect(settings.RABBITMQ_BROKER_URL)

    async with connection:
        # Creating a channel
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            "CQRS_EVENT_STORE", type="topic", durable=True
        )

        # Declaring queue
        queue = await channel.declare_queue(exclusive=True)

        # Binding the queue to the exchange
        await queue.bind(exchange, "parking.create")

        # Start listening the queue
        await queue.consume(on_message)

        logging.info("Event consumer for parking slot replication is running...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
