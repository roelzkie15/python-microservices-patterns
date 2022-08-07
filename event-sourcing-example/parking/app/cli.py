import fire

from app.db import Session
from app.services import (create_parking_slot, parking_slot_details,
                          parking_slot_list)


class AppCLI(object):
    async def create_parking_slot(self, name: str, status: str | None = "available"):
        with Session() as session:
            ps = await create_parking_slot(session, name=name, status=status)
            return ps.to_dict()

    async def parking_slot_list(self):
        with Session() as session:
            ps_list = await parking_slot_list(session)
            return [ps.to_dict() for ps in ps_list]

    async def parking_slot_details(self, uuid: str):
        with Session() as session:
            ps = await parking_slot_details(session, uuid)
            return ps.to_dict()


if __name__ == "__main__":
    fire.Fire(AppCLI)
