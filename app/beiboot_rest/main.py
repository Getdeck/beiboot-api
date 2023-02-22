import logging

import kubernetes as k8s
import uvicorn
from config import settings
from fastapi import Depends, FastAPI, Header
from routers import clusters, configs, connections
from routers.configs import update_cluster_config

logger = logging.getLogger("uvicorn.beiboot")


def user_headers(
    x_forwarded_user: str | None = Header(),
    x_forwarded_groups: str | None = Header(default=None),
    x_forwarded_email: str | None = Header(default=None),
    x_forwarded_preferred_username: str | None = Header(default=None),
):
    return {
        "X-Forwarded-User": x_forwarded_user,
        "X-Forwarded-Groups": x_forwarded_groups,
        "X-Forwarded-Email": x_forwarded_email,
        "X-Forwarded-Preferred-Username": x_forwarded_preferred_username,
    }


app = FastAPI(dependencies=[Depends(user_headers)])
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


@app.get("/")
async def get_root():
    return {"Beiboot": "API"}


@app.get("/sentry-debug/")
async def trigger_error():
    _ = 1 / 0


app.include_router(configs.router)
app.include_router(clusters.router)
app.include_router(connections.router)


def start():
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
