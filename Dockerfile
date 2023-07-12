FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /auth

RUN apt-get update
RUN apt-get install --no-install-recommends -y netcat-openbsd curl build-essential

RUN pip install pipenv mock pytest mypy flake8 autoflake
COPY Pipfile .

ENV PIPENV_VENV_IN_PROJECT=1

RUN pipenv install
RUN pipenv sync --system

COPY . .

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
