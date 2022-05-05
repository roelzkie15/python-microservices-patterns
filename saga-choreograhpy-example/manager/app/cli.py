import fire

from app.db import SQLModel, engine


class BookingAppEngine:

    def create_all_tables(self):
        SQLModel.metadata.create_all(engine)

    def drop_all_tables(self):
        SQLModel.metadata.drop_all(engine)


if __name__ == '__main__':
    fire.Fire(BookingAppEngine)
