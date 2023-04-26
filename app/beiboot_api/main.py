import logging
from typing import Annotated

import kubernetes as k8s
import uvicorn
from config import Settings, get_settings
from exceptions import BeibootException
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from routers import clusters, configs, connections, debug
from routers.configs import update_cluster_config
from sentry import sentry_setup
from sentry_sdk import capture_exception

logger = logging.getLogger("uvicorn.beiboot")


app = FastAPI()
app.cluster_configs = {}


def setup_kubeconfig(config_file: str) -> None:
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
        k8s.config.load_kube_config(config_file=config_file)
        logger.info(f"Loaded local config: '{config_file}'.")
    except k8s.config.ConfigException:
        pass
    else:
        return None

    logger.error("Kubeconfig setup failed.")


@app.on_event("startup")
async def startup_event():
    settings = get_settings()

    # setup sentry
    sentry_setup(dsn=settings.sentry_dsn, environment=settings.sentry_environment)

    # setup kubeconfig
    setup_kubeconfig(config_file=settings.k8s_config_file)

    # setup cluster config
    try:
        update_cluster_config()
    except Exception:
        logger.error(f"Loading default configmap '{settings.cc_default_name}' failed.")


@app.exception_handler(BeibootException)
async def beiboot_exception_handler(request: Request, exc: BeibootException):
    capture_exception(exc)  # sentry

    return JSONResponse(
        status_code=500,
        content={"msg": exc.message},
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
