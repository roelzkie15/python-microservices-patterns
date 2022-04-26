
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.amqp_client import AMQPClient
from app.schema import schema

app = FastAPI()

graphql_app = GraphQLRouter(schema)

@app.on_event('startup')
async def startup():
    app.state.booking_event_store = await AMQPClient('BOOKING_EVENT_STORE').init()

@app.on_event('shutdown')
async def shutdown():
    await app.state.booking_event_store.connection.close()


app.include_router(graphql_app, prefix='/graphql')
