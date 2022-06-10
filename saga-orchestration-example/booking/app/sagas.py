import ast
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


class SagaReplyHandler:

    reply_status: str | None
    action: Callable[P, T] | None
    compensation: Callable[P, T] | None

    def __init__(
        self, reply_status: str, action: Callable[P, T] | None,
        compensation: Callable[P, T] | None
    ) -> None:
        self.reply_status = reply_status
        self.action = action
        self.compensation = compensation


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
            await self.callback_queue.consume(self.reply_event_processor)

            yield self

        finally:
            await self.connection.close()

    def reply_event_processor(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f'Bad message {message!r}')
            return

        try:
            future: asyncio.Future = self.futures.pop(message.correlation_id)
            future.set_result(message.body)
        except KeyError:
            print(f'Unknown correlation_id! - {message.correlation_id}')

    async def start_workflow(self) -> Any:
        for step_definition in await self.definitions:
            is_step_success = await step_definition
            if not is_step_success:
                break

    async def invoke_local(self, action: Callable[P, T]):
        return await action()

    async def invoke_participant(
        self, command: str, on_reply: List[SagaReplyHandler] | None
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

        # Wait for the reply event processor to received a reponse from
        # the participating service.
        reponse_data = await future

        # If response reply status execute a compensation command
        # we need to stop the succeeding step by returning `False`.
        is_success = True
        for reply_handler in on_reply:
            saga_reply_handler: SagaReplyHandler = reply_handler
            if reponse_data.reply_state == saga_reply_handler.reply_status:

                if saga_reply_handler.action is not None:
                    await saga_reply_handler.action

                if saga_reply_handler.compensation is not None:
                    await saga_reply_handler.compensation
                    is_success = False

        return is_success

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
            self.invoke_local(
                action=self.create_booking
            ),
            self.invoke_participant(
                command='parking.check_availability',
                on_reply=[
                    SagaReplyHandler(
                        'PARKING_AVAILABLE',
                        action=self.approve_booking
                    ),
                    SagaReplyHandler(
                        'PARKING_UNAVAILABLE',
                        compensation=self.disapprove_booking
                    )
                ]
            ),
            self.invoke_participant(
                command='bill.create',
                on_reply=[
                    SagaReplyHandler('BILL_CREATED', action=self.bill_booking)
                ]
            ),
        ]

    async def create_booking(self):
        # with Session() as session:
        #     booking = await create_booking(session, self.data)
        #     return booking.id is not None
        return True

    async def disapprove_booking(self):
        return False

    async def parking_available(self):
        pass

    async def approve_booking(self):
        pass

    async def bill_booking(self):
        pass
