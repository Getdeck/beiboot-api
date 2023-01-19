# base
FROM python:3.10-slim AS base

RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
        curl git python3-pip libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# venv builder
FROM base AS builder
WORKDIR /app

RUN pip install --upgrade pip

#COPY --from=requirement /requirements.txt /requirements.txt
COPY ./pyproject.toml ./poetry.lock* ./
COPY api /app/api
RUN pip install -e .

# fastapi
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN adduser --system --no-create-home user
USER user

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
