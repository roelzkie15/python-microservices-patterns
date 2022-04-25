
from fastapi import Depends, FastAPI

from app.amqp_client import AMQPClient
from app.dependencies import get_settings
from app.services import notify_user, update_booking_status_from_event
from app.settings import Settings

app = FastAPI()


@app.on_event('startup')
async def startup():
   app.state.amqp_client = await AMQPClient('BOOKING_EVENT_STORE').init()

   await app.state.amqp_client.event_consumer(
       update_booking_status_from_event, 'invoice.generated', 'invoice_file_event_queue'
   )

   await app.state.amqp_client.event_consumer(
       notify_user, 'invoice.failed',
   )

@app.get('/')
async def root(settings: Settings = Depends(get_settings)):
    return {'message': 'Hello World'}


# TODO: Remove this path later.
@app.get('/publish')
async def publish():
    await app.state.amqp_client.event_producer(
        'BOOKING_EVENT_STORE',
        "{'message': 'Booking reserved!'}",
        'invoice.generated'
    )
    return {'message': 'published'}
