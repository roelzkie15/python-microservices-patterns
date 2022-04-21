from fastapi import Depends, FastAPI

from app.settings import Settings
from app.dependencies import get_settings
from app.redis import redis

app = FastAPI()

@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"message": "Hello World"}
