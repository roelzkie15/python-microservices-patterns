from fastapi import Depends, FastAPI

from app.dependencies import get_settings
from app.settings import Settings

app = FastAPI()


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"message": "Hello World"}
