from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def startup_event():
    pass


async def shutdown_event():
    pass


async def root(request):
    return JSONResponse({'message': 'Parking server is running'})

routes = [
    Route('/', root),
]

app = Starlette(
    routes=routes,
    on_startup=[startup_event],
    on_shutdown=[shutdown_event]
)