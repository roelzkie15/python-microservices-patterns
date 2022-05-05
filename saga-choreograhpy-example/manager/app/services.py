from aio_pika import IncomingMessage

async def create_booking_request(message : IncomingMessage):
    print(message.body.decode())
    await message.ack()
