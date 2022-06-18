import ast
import contextlib

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.amqp_client import AMQPClient
from app.services import billing_command_event_processor


@contextlib.asynccontextmanager
async def lifespan(app):
    amqp_client: AMQPClient = await AMQPClient().init()
    try:

        await amqp_client.event_consumer(billing_command_event_processor, 'BOOKING_TX_EVENT_STORE', 'billing.*')

        yield
    finally:
        await amqp_client.connection.close()


async def health(request):
    return JSONResponse({'message': 'Billing server is running'})


routes = [
    Route('/health', health),
]

app = Starlette(routes=routes, lifespan=lifespan)
