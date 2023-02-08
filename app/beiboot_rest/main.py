import logging

import kubernetes as k8s
import uvicorn
from beiboot_rest.routers import clusters, configs
from beiboot_rest.routers.configs import update_beiboot_rest_config
from config import settings
from fastapi import FastAPI

logger = logging.getLogger("uvicorn.beiboot")

try:
    k8s.config.load_incluster_config()
    logger.info("Loaded in-cluster config")
except k8s.config.ConfigException:
    # if the api is executed locally, expecting a "kubeconfig.yaml"
    k8s.config.load_kube_config(config_file="./kubeconfig.yaml")
    logger.info("Loaded KUBECONFIG config")


app = FastAPI()
app.rest_configs = {}


@app.on_event("startup")
async def startup_event():
    # setup rest config
    try:
        update_beiboot_rest_config()
    except Exception:
        logger.error(f"Loading configmap '{settings.rc_default_name}' failed")


@app.get("/")
async def get_root():
    return {"Beiboot": "API"}


@app.get("/sentry-debug/")
async def trigger_error():
    _ = 1 / 0


app.include_router(configs.router)
app.include_router(clusters.router)


def start():
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
