import asyncio
from sqlalchemy import event

from app.amqp_client import AMQPClient
from app.models import AMQPMessage, ParkingSlot
from app.pydantic_models import PydanticParkingSlot


@event.listens_for(ParkingSlot, 'after_update')
def parking_slot_receive_after_update(mapper, connection, target: ParkingSlot):
    asyncio.ensure_future(async_parking_slot_receive_after_update(mapper, connection, target))

async def async_parking_slot_receive_after_update(mapper, connection, target):
    if target.status == 'reserved':
        amqp_client: AMQPClient = await AMQPClient().init()
        pydantic_parking_slot = PydanticParkingSlot.from_orm(target)
        await amqp_client.event_producer(
            'BOOKING_TX_EVENT_STORE', 'parking.reserved',
            message=AMQPMessage(
                id=str(target.uuid), content={'status': 'reserved'}
            )
        )
        await amqp_client.connection.close()
