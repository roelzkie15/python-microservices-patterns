import asyncio
import contextlib
from typing import (Any, Callable, Coroutine, List, MutableMapping, ParamSpec,
                    TypeVar)
from uuid import uuid4

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage

from app import settings
from app.models import Booking

P = ParamSpec('P')
T = TypeVar('T')


class SagaRPC:

    data: Any = None

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()

    @contextlib.contextmanager
    async def connect(self) -> "SagaRPC":
        try:
            self.connection = await connect_robust(
                settings.RABBITMQ_BROKER_URL, loop=self.loop,
            )
            self.channel = await self.connection.channel()
            self.callback_queue = await self.channel.declare_queue(exclusive=True)
            await self.callback_queue.consume(self.on_response)

            yield self

        finally:
            self.connection.close()

    def on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f'Bad message {message!r}')
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def start_workflow(self) -> Any:
        for step_definition in self.definitions:
            step_result = await step_definition
            if not step_result:
                break

    async def invoke_local(self, func: Callable[P, T], on_reply: List[tuple[str, Callable[P, T]]] | None):
        return func(self.data)

    async def invoke_participant(
        self, command_name: str, on_reply: List[tuple[str, Callable[P, T]]] | None
    ) -> bool:

        correlation_id = str(uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        exchange = await self.channel.declare_exchange(
            exchange,
            type='topic',
            durable=True
        )

        await exchange.publish(
            Message(
                str(self.data).encode(),
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=command_name,
        )

        reponse_data = await future

        for reply_handler in on_reply:
            expected_state, reply_processor = reply_handler
            if reponse_data.reply_state == expected_state:
                reply_processor(reponse_data)
                return False

        return True

    @property
    async def definitions(self) -> List[Coroutine]:
        raise NotImplementedError


class CreateBookingRequestSaga(SagaRPC):

    def __init__(self, bookingData: Booking) -> None:
        self.data: Booking = bookingData

    @property
    async def definitions(self):
        return [
            self.invoke_local(self.create_booking),
            self.invoke_participant(
                command_name='parking.check_availability',
                on_reply=[
                    ('PARKING_UNAVAILABLE', self.parking_unavailable),
                ]
            ),
            self.invoke_local(self.approve_booking),
            self.invoke_participant(
                command_name='bill.create'
            ),
            self.invoke_local(self.billed_booking),
        ]

    def create_booking(self, data):
        pass

    def parking_unavailable(self, data):
        pass

    def approve_booking(self):
        pass

    def billed_booking(self):
        pass
