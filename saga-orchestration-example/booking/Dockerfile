FROM python:3.10.3-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update

RUN pip install -U \
    pip \
    setuptools \
    wheel

RUN pip --no-cache-dir install poetry

WORKDIR /code

RUN poetry config virtualenvs.in-project false

COPY pyproject.toml .
RUN poetry lock && poetry install

COPY . .

CMD ["chmod", "+x", "/code/start_dev.sh", '/code/wait-for-it.sh']

