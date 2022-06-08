import asyncio
import contextlib
from typing import (Any, Callable, Coroutine, List, MutableMapping, ParamSpec,
                    TypeVar)
from uuid import uuid4

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage

from app import settings
from app.db import Session
from app.models import Booking
from app.services import create_booking

P = ParamSpec('P')
T = TypeVar('T')


class SagaRPC:

    data: Any = None

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()

    @contextlib.asynccontextmanager
    async def connect(self) -> "SagaRPC":
        try:
            self.connection = await connect_robust(
                settings.RABBITMQ_BROKER_URL, loop=self.loop,
            )
            self.channel = await self.connection.channel()

            self.exchange = await self.channel.declare_exchange(
                'BOOKING_TX_EVENT_STORE',
                type='topic',
                durable=True
            )

            self.callback_queue = await self.channel.declare_queue(exclusive=True)
            await self.callback_queue.bind(self.exchange)
            await self.callback_queue.consume(self.on_response)

            yield self

        finally:
            await self.connection.close()

    def on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f'Bad message {message!r}')
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def start_workflow(self) -> Any:
        for step_definition in await self.definitions:
            is_step_success = await step_definition
            if not is_step_success:
                break

    async def invoke_local(self, func: Callable[P, T]):
        return await func()

    async def invoke_participant(
        self, command: str, on_reply: List[tuple[str, Callable[P, T]]] | None
    ) -> bool:

        correlation_id = str(uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.exchange.publish(
            Message(
                str(self.data).encode(),
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=command,
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

    subject: Booking = None

    def __init__(self, parking_slot_uuid: str) -> None:
        super().__init__()
        self.data: str = parking_slot_uuid

    @property
    async def definitions(self):
        return [
            self.invoke_local(self.create_booking),
            self.invoke_participant(
                command='parking.check_availability',
                on_reply=[
                    ('PARKING_AVAILABLE', self.parking_available),
                    ('PARKING_UNAVAILABLE', self.parking_unavailable),
                ]
            ),
            self.invoke_local(self.approve_booking),
            self.invoke_participant(
                command='bill.create',
                on_reply=(
                    ('BILL_CREATED', self.bill_created)
                )
            ),
            self.invoke_local(self.billed_booking),
        ]

    async def create_booking(self):
        # with Session() as session:
        #     booking = await create_booking(session, self.data)
        #     return booking.id is not None
        return True

    def parking_unavailable(self):
        pass

    def parking_available(self):
        pass

    def approve_booking(self):
        pass

    def bill_created(self):
        pass

    def billed_booking(self):
        pass
