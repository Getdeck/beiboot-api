import logging

import kubernetes as k8s
from beiboot import api
from beiboot.types import BeibootParameters, BeibootRequest
from config import settings
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sentry import sentry_setup
from type import ClusterCreateData

sentry_setup(dsn=settings.sentry_dsn, environment=settings.sentry_environment)

logger = logging.getLogger("beiboot")
logger.info("Beiboot REST API startup")

try:
    k8s.config.load_incluster_config()
    logger.info("Loaded in-cluster config")
except k8s.config.ConfigException:
    # if the api is executed locally, expecting a "kubeconfig.yaml"
    k8s.config.load_kube_config(config_file=settings.config_file_location)
    logger.info("Loaded KUBECONFIG config")

app = FastAPI()


@app.get("/")
async def get_root():
    return {"Beiboot": "API"}


@app.get("/sentry-debug/")
async def trigger_error():
    _ = 1 / 0


@app.post("/cluster/")
async def cluster_create(data: ClusterCreateData):
    req = BeibootRequest(
        name=data.name,
        parameters=BeibootParameters(
            nodes=1,
            serverStorageRequests="500Mi",
            serverResources={"requests": {"cpu": "0.25", "memory": "0.25Gi"}},
            nodeResources={"requests": {"cpu": "0.25", "memory": "0.25Gi"}},
        ),
    )
    beiboot = api.create(req=req)

    response = JSONResponse(content={"state": beiboot.state})
    return response


@app.delete("/cluster/{name}")
async def cluster_delete(name: str):
    response = JSONResponse(content={})
    return response


@app.get("/cluster/{name}/state")
async def cluster_state(name: str):
    beiboot = api.read(name)
    response = JSONResponse(content={"state": beiboot.state})
    return response


@app.get("/cluster/{name}/kubeconfig")
async def cluster_kubeconfig(name: str):
    response = JSONResponse(content={})
    return response


@app.get("/cluster/{name}/mtls")
async def cluster_mtls(name: str):
    response = JSONResponse(content={})
    return response
