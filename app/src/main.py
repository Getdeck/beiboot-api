import logging
from uuid import UUID

from config import settings
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sentry import sentry_setup
from type import ClusterData

logger = logging.getLogger()

sentry_setup(dns=settings.sentry_dsn, environment=settings.sentry_environment)

app = FastAPI()


@app.get("/")
async def get_root():
    return {"Beiboot": "API"}


@app.get("/sentry-debug/")
async def trigger_error():
    _ = 1 / 0


@app.post("/cluster/")
async def cluster_create(data: ClusterData):
    print(data)
    response = JSONResponse(content={})
    return response


@app.delete("/cluster/{uuid}")
async def cluster_delete(uuid: UUID):
    print(uuid)
    response = JSONResponse(content={})
    return response
