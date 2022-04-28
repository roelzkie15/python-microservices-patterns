from typing import Any

from attrs import define


@define
class Booking:
    uuid: str
    name: str
    status: str = 'created'


@define
class AMQPMessage:
    id: str
    body: Any
