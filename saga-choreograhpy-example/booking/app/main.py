
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.amqp_client import AMQPClient
from app.schema import schema
from app.services import test_consume

app = FastAPI()


@app.on_event('startup')
async def startup():
    amqp_client:AMQPClient = await AMQPClient().init()

    await amqp_client.event_store('BOOKING_EVENT_STORE')
    await amqp_client.event_store('MANAGER_EVENT_STORE')

    await amqp_client.event_consumer(test_consume, 'booking.created', 'booking_events')

    app.state.amqp_client = amqp_client

@app.on_event('shutdown')
async def shutdown():
    await app.state.amqp_client.connection.close()


async def get_context():
    return {
        'amqp_client': app.state.amqp_client
    }


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix='/graphql')
