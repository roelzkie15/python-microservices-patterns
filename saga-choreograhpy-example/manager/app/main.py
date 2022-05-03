

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


app = FastAPI()


@app.on_event('startup')
async def startup():
   pass


@app.on_event('shutdown')
async def shutdown():
    pass

@app.get('/health')
async def root():
    return {'message': 'Manager server is running'}


# async def get_context():
#     return {
#         'amqp_client': app.state.amqp_client
#     }


# graphql_app = GraphQLRouter(schema, context_getter=get_context)
# app.include_router(graphql_app, prefix='/graphql')
