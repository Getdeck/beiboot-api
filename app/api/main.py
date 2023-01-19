import logging
from typing import List
from uuid import UUID

import kubernetes as k8s
import uvicorn
from api.config import settings
from api.sentry import sentry_setup
from api.type import BeibootResponse, ClusterData
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from beiboot import api
from beiboot.types import BeibootRequest, BeibootParameters

# sentry_setup(dns=settings.sentry_dsn, environment=settings.sentry_environment)

logger = logging.getLogger("beiboot")
logger.info("Beiboot REST API startup")

try:
    k8s.config.load_incluster_config()
    logger.info("Loaded in-cluster config")
except k8s.config.ConfigException:
    # if the api is executed locally, expecting a "kubeconfig.yaml"
    k8s.config.load_kube_config(config_file="./kubeconfig.yaml")
    logger.info("Loaded KUBECONFIG config")

app = FastAPI()


@app.get("/")
async def get_root():
    return {"Beiboot": "API"}


@app.get("/sentry-debug/")
async def trigger_error():
    _ = 1 / 0


@app.get("/cluster/", response_model=List[BeibootResponse])
async def cluster_list() -> List[BeibootResponse]:
    beiboots = api.read_all()

    response = []
    for beiboot in beiboots:
        response.append(BeibootResponse(name=beiboot.name, state=beiboot.state))
    return response


@app.post("/cluster/", response_model=BeibootResponse)
async def cluster_create(data: ClusterData) -> BeibootResponse:
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
    response = BeibootResponse(name=beiboot.name, state=beiboot.state)
    return response


@app.delete("/cluster/{name}", response_model=BeibootResponse)
async def cluster_delete(name: str) -> BeibootResponse:
    api.delete_by_name(name=name)
    return JSONResponse(content={})


@app.get("/cluster/{name}/state", response_model=BeibootResponse)
async def cluster_state(name: str) -> BeibootResponse:
    beiboot = api.read(name=name)
    response = BeibootResponse(name=beiboot.name, state=beiboot.state)
    return response


@app.get("/cluster/{name}/kubeconfig")
async def cluster_kubeconfig(name: str):
    response = JSONResponse(content={})
    return response


@app.get("/cluster/{name}/mtls")
async def cluster_mtls(name: str):
    response = JSONResponse(content={})
    return response


def start():
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
