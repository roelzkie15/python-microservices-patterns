from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def root(request):
    return JSONResponse({'message': 'Booking server is running'})

routes = [
    Route('/', root),
]

app = Starlette(
    routes=routes
)
