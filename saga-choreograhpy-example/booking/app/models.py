from typing import Any

from pydantic import BaseModel


class AMQPMessage(BaseModel):
    id: str
    body: Any
