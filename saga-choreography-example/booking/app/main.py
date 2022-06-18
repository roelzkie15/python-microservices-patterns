

from fastapi import FastAPI

from app.amqp_client import AMQPClient
from app.services import set_booking_to_status_from_event

app = FastAPI()


@app.on_event('startup')
async def startup():
    amqp_client: AMQPClient = await AMQPClient().init()

    await amqp_client.event_consumer(set_booking_to_status_from_event, 'BOOKING_TX_EVENT_STORE', 'parking.reserved', 'parking_events')
    await amqp_client.event_consumer(set_booking_to_status_from_event, 'BOOKING_TX_EVENT_STORE', 'parking.unavailable')

    app.state.amqp_client = amqp_client


@app.on_event('shutdown')
async def shutdown():
    await app.state.amqp_client.connection.close()


@app.get('/health')
async def root():
    return {'message': 'Booking server is running'}
