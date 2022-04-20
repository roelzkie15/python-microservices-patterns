from fastapi import Depends, FastAPI

from app.config import Settings
from app.dependencies import get_settings

app = FastAPI()


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"message": "Hello World"}
