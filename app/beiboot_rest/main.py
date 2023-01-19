import logging
from uuid import UUID

import kubernetes as k8s
import uvicorn

from fastapi import FastAPI
from beiboot_rest.routers import clusters
from beiboot_rest.sentry import sentry_setup

# sentry_setup(dns=settings.sentry_dsn, environment=settings.sentry_environment)

logger = logging.getLogger("uvicorn.beiboot")
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


app.include_router(clusters.router)

def start():
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
