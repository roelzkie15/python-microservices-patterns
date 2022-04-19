FROM python:3.10.4-slim-buster

ENV PYTHONUNBUFFERED 1

RUN pip install -U \
    pip \
    setuptools \
    wheel
RUN pip install poetry

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

RUN poetry config virtualenvs.in-project false
RUN poetry install --no-root

COPY . /code

CMD ["chmod", "+x", "/code/start_dev.sh"]

