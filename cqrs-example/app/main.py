from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def health(request):
    return JSONResponse({"message": "CQRS server is running..."})


routes = [
    Route("/health", health),
]

app = Starlette(routes=routes)
