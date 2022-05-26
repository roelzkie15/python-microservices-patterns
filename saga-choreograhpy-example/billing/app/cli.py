
from decimal import Decimal

import fire

from app.amqp_client import AMQPClient
from app.db import Session
from app.models import AMQPMessage
from app.services import (billing_request_details_by_reference_no,
                          billing_request_list, create_payment_reconciliation,
                          update_billing_request)


class AppCLI(object):

    async def billing_request_list(self):
        with Session() as session:
            br_list = await billing_request_list(session)
            return [
                dict(
                    (col, getattr(br, col))
                    for col in br.__table__.columns.keys()
                )
                for br in br_list
            ]

    async def billing_request_details_by_reference_no(self, ref_no: str):
        with Session() as session:
            billing_request = await billing_request_details_by_reference_no(session, ref_no=ref_no)
            billing_request_obj = {
                'billing_request': dict(
                    (col, getattr(billing_request, col))
                    for col in billing_request.__table__.columns.keys()
                ),
                'reconciliations': [
                    dict(
                        (col, getattr(payment, col))
                        for col in payment.__table__.columns.keys()
                    )
                    for payment in billing_request.payment_reconciliations
                ]
            }
            return billing_request_obj

    async def pay_bill(self, ref_no: str, amount: Decimal):
        with Session() as session:
            billing_request = await billing_request_details_by_reference_no(session, ref_no=ref_no)
            billing_request_obj = dict(
                (col, getattr(billing_request, col))
                for col in billing_request.__table__.columns.keys()
            )

            if billing_request.status == 'paid':
                return 'Billing request already paid.'

            # To avoid complex logic we will only accept sufficient payment.
            total_payment = billing_request.calculate_total_payment(amount)
            if total_payment > billing_request.total:
                return f'Payment is over {total_payment - billing_request.total}.\nUnable to process payment transaction.'

            reconciliation = await create_payment_reconciliation(
                session, billing_request.id, amount
            )
            reconciliation_obj = dict(
                (col, getattr(reconciliation, col))
                for col in reconciliation.__table__.columns.keys()
            )

            if billing_request.balance == Decimal('0.0'):
                billing_request.status = 'paid'
                billing_request = await update_billing_request(session, billing_request)

                amqp_client: AMQPClient = await AMQPClient().init()
                await amqp_client.event_producer(
                    'BOOKING_TX_EVENT_STORE', 'bill.paid', message=AMQPMessage(id=str(billing_request.reference_no), content=billing_request_obj)
                )

            return reconciliation_obj


if __name__ == '__main__':
  fire.Fire(AppCLI)
