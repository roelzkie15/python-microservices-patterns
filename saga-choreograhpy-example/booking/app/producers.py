from aio_pika import Message

from app.pika_client import init_pika_client


async def event_producers(event: str, message) -> None:
    conn = await init_pika_client()
    async with conn:
        # Creating channel
        channel = await conn.channel()

        # Declare exchange
        exchange = await channel.declare_exchange(
            'BOOKING_SERVICE_EXCHANGE',
            type='topic'
        )

        await exchange.publish(
            Message(
                body="{'status': 'reserved!'}".encode(),
                content_type="application/json",
                headers={"foo": "bar"},
            ),
            routing_key=event,
        )
