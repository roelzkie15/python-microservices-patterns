
from fastapi import Depends, FastAPI

from app.consumers import init_consumers
from app.dependencies import get_settings
from app.pika_client import init_pika_client
# from app.producers import event_producer
from app.settings import Settings

app = FastAPI()


@app.on_event('startup')
async def startup():
    await init_pika_client(app)
    await init_consumers(app)


@app.get('/')
async def root(settings: Settings = Depends(get_settings)):
    return {'message': 'Hello World'}


# TODO: Remove this path later.
# @app.get('/publish')
# async def publish():
#     await event_producer(
#         app, 'BOOKING_SERVICE_EXCHANGE',
#         "{'message': 'Booking reserved!'}",
#     )
#     return {'message': 'published'}
