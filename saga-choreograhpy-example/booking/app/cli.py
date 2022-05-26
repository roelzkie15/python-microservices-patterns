
import fire

from app.db import Session
from app.services import (booking_details_by_parking_slot_uuid, booking_list,
                          create_booking)
from app.amqp_client import AMQPClient
from app.models import AMQPMessage


class AppCLI(object):

    async def create_booking(self, parking_slot_uuid):
        with Session() as session:
            booking = await create_booking(session, parking_slot_uuid)

            obj = dict((col, getattr(booking, col))
                       for col in booking.__table__.columns.keys())

            amqp_client: AMQPClient = await AMQPClient().init()
            await amqp_client.event_producer(
                'BOOKING_TX_EVENT_STORE', 'booking.created', message=AMQPMessage(id=str(booking.parking_slot_uuid), content=obj)
            )
            await amqp_client.connection.close()

            return obj

    async def booking_list(self):
        with Session() as session:
            b_list = await booking_list(session)
            return [
                dict((col, getattr(booking, col))
                     for col in booking.__table__.columns.keys())
                for booking in b_list
            ]

    async def booking_details_by_parking_slot_uuid(self, uuid: str):
        with Session() as session:
            booking = await booking_details_by_parking_slot_uuid(session, uuid)
            return dict((col, getattr(booking, col)) for col in booking.__table__.columns.keys())


if __name__ == '__main__':
  fire.Fire(AppCLI)
