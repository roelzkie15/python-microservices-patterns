import aio_pika


async def set_booking_status(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():
        message.ack()
        print(message.body)
