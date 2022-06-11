import fire

from app.db import Session
from app.services import billing_request_list


class AppCLI(object):

    async def billing_request_list(self):
        with Session() as session:
            br_list = await billing_request_list(session)
            return [br.to_dict() for br in br_list]


if __name__ == '__main__':
  fire.Fire(AppCLI)
