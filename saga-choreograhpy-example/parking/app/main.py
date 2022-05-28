from fastapi import FastAPI

from app.amqp_client import AMQPClient
from app.services import update_parking_slot_to_reserved_by_ref_no

app = FastAPI()


@app.on_event('startup')
async def startup():
    amqp_client: AMQPClient = await AMQPClient().init()

    await amqp_client.event_consumer(update_parking_slot_to_reserved_by_ref_no, 'BOOKING_TX_EVENT_STORE', 'bill.paid', 'billing_events')

    app.state.amqp_client = amqp_client


@app.on_event('shutdown')
async def shutdown():
    await app.state.amqp_client.connection.close()


@app.get('/health')
async def root():
    return {'message': 'Manager server is running'}
