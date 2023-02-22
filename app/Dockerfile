ARG PYTHON_VERSION="3.10"
ARG POETRY_VERSION="1.3.2"

# base
FROM python:${PYTHON_VERSION}-alpine AS base

RUN apk update && apk upgrade
RUN pip install --upgrade pip

# requirement
FROM base AS requirement
ARG POETRY_VERSION

ENV POETRY_HOME="/opt/poetry"
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==${POETRY_VERSION}

COPY ./pyproject.toml ./poetry.lock* ./
RUN $POETRY_HOME/bin/poetry export -f requirements.txt --output requirements.txt --without-hashes

# builder
FROM python:${PYTHON_VERSION} AS builder

ENV VENV_HOME="/opt/venv"
RUN python3 -m venv $VENV_HOME

COPY --from=requirement /requirements.txt /requirements.txt
RUN $VENV_HOME/bin/pip install -r requirements.txt

# fastapi
FROM base AS fastapi

ENV VENV_HOME="/opt/venv"
COPY --from=builder $VENV_HOME $VENV_HOME

ENV PYTHONPATH="/app:$VENV_HOME" \
    PATH="$VENV_HOME/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY beiboot_rest /app
WORKDIR /app

RUN adduser --system --no-create-home user && chown -R user /app
USER user

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
