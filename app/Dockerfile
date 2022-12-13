# base
FROM python:3.10-slim AS base

ARG PANDOC_VERSION=2.18-1-amd64

RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
        curl git python3-pip libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# poetry requirement
FROM python:3.10 AS requirement

RUN pip install --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

COPY ./pyproject.toml ./poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# venv builder
FROM base AS builder

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

COPY --from=requirement /requirements.txt /requirements.txt
RUN pip install -r requirements.txt

# fastapi
FROM base AS fastapi

COPY --from=builder /opt/venv /opt/venv

ENV PYTHONPATH=/app:/opt/venv \
    PATH=/opt/venv/bin/:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY src /app
WORKDIR /app

RUN adduser --system --no-create-home user && chown -R user /app
USER user

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]