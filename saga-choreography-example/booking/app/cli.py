
import fire

from app.amqp_client import AMQPClient
from app.db import Session
from app.models import AMQPMessage
from app.services import (booking_details_by_parking_ref_no, booking_list,
                          create_booking)


class AppCLI(object):

    async def create_booking(self, parking_slot_uuid):
        with Session() as session:
            booking = await create_booking(session, parking_slot_uuid)

            obj = booking.to_dict()

            amqp_client: AMQPClient = await AMQPClient().init()
            await amqp_client.event_producer(
                'BOOKING_TX_EVENT_STORE', 'booking.created', message=AMQPMessage(id=booking.parking_slot_ref_no, content=obj)
            )
            await amqp_client.connection.close()

            return obj

    async def booking_list(self):
        with Session() as session:
            b_list = await booking_list(session)
            return [
                booking.to_dict() for booking in b_list
            ]

    async def booking_details_by_parking_ref_no(self, uuid: str):
        with Session() as session:
            booking = await booking_details_by_parking_ref_no(session, uuid)
            return booking.to_dict()


if __name__ == '__main__':
  fire.Fire(AppCLI)
