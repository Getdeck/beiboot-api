ARG PYTHON_VERSION="3.10"
ARG POETRY_VERSION="1.4.0"

# base
FROM python:${PYTHON_VERSION}-slim AS base
RUN apt-get update && apt-get upgrade -y \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# requirement
FROM python:${PYTHON_VERSION} AS requirement
ARG POETRY_VERSION
ARG POETRY_HOME="/opt/poetry"

RUN apt-get update && apt-get upgrade -y \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv ${POETRY_HOME}
RUN ${POETRY_HOME}/bin/pip install --upgrade pip
RUN ${POETRY_HOME}/bin/pip install poetry==${POETRY_VERSION}

COPY ./pyproject.toml ./poetry.lock* ./
RUN ${POETRY_HOME}/bin/poetry export -f requirements.txt --output requirements.txt --without-hashes

# builder
FROM base AS builder
ARG VENV_HOME="/opt/venv"

RUN python3 -m venv ${VENV_HOME}
RUN ${VENV_HOME}/bin/pip install --upgrade pip

COPY --from=requirement /requirements.txt /requirements.txt
RUN ${VENV_HOME}/bin/pip install -r requirements.txt

# fastapi
FROM base AS fastapi
ARG VENV_HOME="/opt/venv"

COPY --from=builder ${VENV_HOME} ${VENV_HOME}

ENV PYTHONPATH="/app:${VENV_HOME}" \
    PATH="${VENV_HOME}/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY beiboot_rest /app
WORKDIR /app

RUN adduser --system --no-create-home user && chown -R user /app
USER user

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
