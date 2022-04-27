
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.amqp_client import AMQPClient
from app.schema import schema

app = FastAPI()


@app.on_event('startup')
async def startup():
    app.state.amqp_client = await AMQPClient().init()
    await app.state.amqp_client.event_store('BOOKING_EVENT_STORE')


@app.on_event('shutdown')
async def shutdown():
    await app.state.amqp_client.connection.close()


async def get_context():
    return {
        'amqp_client': app.state.amqp_client,
    }


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix='/graphql')
