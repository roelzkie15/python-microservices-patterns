import ast
import asyncio
import contextlib
from email import header
from typing import (Any, Callable, Coroutine, List, MutableMapping, ParamSpec,
                    TypeVar)
from uuid import uuid4

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage

from app import settings
from app.db import Session
from app.models import Booking
from app.services import booking_details_by_parking_ref_no, create_booking, update_booking

P = ParamSpec('P')
T = TypeVar('T')


class SagaReplyHandler:

    reply_status: str | None
    action: Coroutine
    is_compensation: bool = False

    def __init__(
        self, reply_status: str, action: Coroutine,
        is_compensation: bool = False
    ) -> None:
        self.reply_status = reply_status
        self.action = action
        self.is_compensation = is_compensation


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

        # If request booking workflow succeeded we can return the data
        return self.data

    async def invoke_local(self, action: Callable[P, T]):
        return await action()

    async def invoke_participant(
        self, command: str, on_reply: List[SagaReplyHandler] | None = None
    ) -> bool:

        if on_reply is None:
            on_reply = []

        correlation_id = str(uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.exchange.publish(
            Message(
                str(self.data.to_dict()).encode(),
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
                headers={
                    'COMMAND': command.replace('.', '_').upper(),
                    'CLIENT': 'BOOKING_REQUEST_ORCHESTRATOR',
                }
            ),
            routing_key=command,
        )

        # Wait for the reply event processor to received a reponse from
        # the participating service.
        response_data: bytes = await future
        decoded_data = ast.literal_eval(response_data.decode('utf-8'))
        reply_state = decoded_data.get('reply_state')

        # If response reply status execute a compensation command
        # we need to stop the succeeding step by returning `False`.
        to_next_definition = True
        for reply_handler in on_reply:
            saga_reply_handler: SagaReplyHandler = reply_handler

            if reply_state == saga_reply_handler.reply_status:
                if saga_reply_handler.is_compensation:
                    to_next_definition = False

                await saga_reply_handler.action

        return to_next_definition

    @property
    async def definitions(self) -> List[Coroutine]:
        raise NotImplementedError


class CreateBookingRequestSaga(SagaRPC):

    data: Booking = None
    parking_slot_uuid: str = None

    def __init__(self, parking_slot_uuid: str) -> None:
        super().__init__()
        self.parking_slot_uuid = parking_slot_uuid

    @property
    async def definitions(self):
        return [
            self.invoke_local(
                action=self.create_booking
            ),
            self.invoke_participant(
                command='parking.reserve',
                on_reply=[
                    SagaReplyHandler(
                        'PARKING_UNAVAILABLE',
                        action=self.invoke_participant(
                            command='parking.unblock'
                        ),
                        is_compensation=True
                    ),
                    SagaReplyHandler(
                        'PARKING_UNAVAILABLE',
                        action=self.invoke_local(self.disapprove_booking),
                        is_compensation=True
                    ),
                ]
            ),
            self.invoke_participant(
                command='billing.create',
                on_reply=[
                    SagaReplyHandler(
                        'BILL_CREATED',
                        action=self.invoke_local(self.bill_booking)
                    )
                ]
            ),
        ]

    async def create_booking(self) -> bool:
        with Session() as session:
            self.data = await create_booking(session, self.parking_slot_uuid)
            return self.data.id is not None

    async def disapprove_booking(self) -> bool:
        return False

    async def bill_booking(self) -> bool:
        with Session() as session:
            booking = await booking_details_by_parking_ref_no(session, self.data.parking_slot_ref_no)
            booking.status = 'billed'

            # Updated data
            self.data = await update_booking(session, booking)
            return self.data.status == 'billed'
