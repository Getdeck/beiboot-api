import logging

import kubernetes as k8s
import uvicorn
from beiboot_rest.routers import clusters, configs, connections, debug
from beiboot_rest.routers.configs import update_cluster_config
from config import settings
from fastapi import FastAPI

logger = logging.getLogger("uvicorn.beiboot")


app = FastAPI()
app.cluster_configs = {}


@app.on_event("startup")
async def startup_event():
    # setup kubeconfig
    try:
        k8s.config.load_incluster_config()
        logger.info("Loaded in-cluster config.")
    except k8s.config.ConfigException:
        k8s.config.load_kube_config(config_file=settings.k8s_config_file)
        logger.info(f"Loaded local config: '{settings.k8s_config_file}'.")

    # setup cluster config
    try:
        update_cluster_config()
    except Exception:
        logger.error(f"Loading configmap '{settings.cc_default_name}' failed.")


@app.get("/")
async def get_root():
    return {"Beiboot": "API"}


app.include_router(clusters.router)
app.include_router(connections.router)
app.include_router(configs.router)
app.include_router(debug.router)


def start():
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
