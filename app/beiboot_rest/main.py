import logging

import kubernetes as k8s
import uvicorn
from config import settings
from exceptions import BeibootException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import clusters, configs, connections, debug
from routers.configs import update_cluster_config

logger = logging.getLogger("uvicorn.beiboot")


app = FastAPI()
app.cluster_configs = {}


def setup_kubeconfig() -> None:
    # incluster config
    try:
        k8s.config.load_incluster_config()
        logger.info("Loaded in-cluster config.")
    except k8s.config.ConfigException:
        pass
    else:
        return None

    # local config
    try:
        k8s.config.load_kube_config(config_file=settings.k8s_config_file)
        logger.info(f"Loaded local config: '{settings.k8s_config_file}'.")
    except k8s.config.ConfigException:
        pass
    else:
        return None

    logger.error("Kubeconfig setup failed.")


@app.on_event("startup")
async def startup_event():
    # setup kubeconfig
    setup_kubeconfig()

    # setup cluster config
    try:
        update_cluster_config()
    except Exception:
        logger.error(f"Loading default configmap '{settings.cc_default_name}' failed.")


@app.exception_handler(BeibootException)
async def beiboot_exception_handler(request: Request, exc: BeibootException):
    # TODO: add error to sentry? -> exc.error

    return JSONResponse(
        status_code=500,
        content={"message": exc.message},
    )


@app.get("/")
async def get_root():
    return {"Beiboot": "API"}


app.include_router(clusters.router)
app.include_router(connections.router)
app.include_router(configs.router)
app.include_router(debug.router)


def start():
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
