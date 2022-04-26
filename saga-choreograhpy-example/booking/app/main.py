
from fastapi import Depends, FastAPI

from app.amqp_client import AMQPClient
from app.dependencies import get_settings
from app.services import notify_user, update_booking_status_from_event
from app.settings import Settings

app = FastAPI()


@app.on_event('startup')
async def startup():
    app.state.booking_event_store = await AMQPClient('BOOKING_EVENT_STORE').init()

    await app.state.booking_event_store.event_consumer(
        update_booking_status_from_event, 'invoice.generated', 'invoice_file_event_queue'
    )

    # Creating a consumer without queue name. It will generate a random name.
    await app.state.booking_event_store.event_consumer(
        notify_user, 'invoice.failed',
    )


@app.get('/')
async def root(settings: Settings = Depends(get_settings)):
    return {'message': 'Hello World'}


# TODO: Remove this path later.
@app.get('/publish')
async def publish():
    await app.state.booking_event_store.event_producer(
        'BOOKING_EVENT_STORE',
        "{'message': 'Booking reserved!'}",
        'invoice.generated'
    )
    return {'message': 'published'}
