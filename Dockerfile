FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && apt-get clean

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

COPY . /app

EXPOSE 8000
