import fire

from app.db import Session
from app.services import (billing_request_details_by_reference_no,
                          billing_request_list, create_billing_request,
                          pay_bill)


class AppCLI(object):

    async def billing_request_list(self):
        with Session() as session:
            br_list = await billing_request_list(session)
            return [br.to_dict() for br in br_list]

    async def billing_request_details_by_reference_no(self, reference_no: str):
        with Session() as session:
            br = await billing_request_details_by_reference_no(session, reference_no)
            return br.to_dict()

    async def create_billing_request(self, reference_no: str):
        with Session() as session:
            br = await create_billing_request(session, reference_no)
            return br.to_dict()

    async def pay_bill(self, reference_no: str):
        # TODO: Shall we convert this to saga?
        with Session() as session:
            br = await pay_bill(session, reference_no)
            return br.to_dict()


if __name__ == '__main__':
  fire.Fire(AppCLI)
