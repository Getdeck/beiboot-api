import logging

import kubernetes as k8s
import timeout_decorator
from config import settings
from fastapi import APIRouter, HTTPException

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/configs", tags=["configs"])

rcs = [
    "cc_cluster_lifetime_limit",
    "cc_cluster_node_limit",
]


@timeout_decorator.timeout(5, timeout_exception=Exception)
def update_cluster_config(name: str = settings.cc_default_name, namespace: str = settings.cc_default_namespace):
    from main import app

    client = k8s.client.CoreV1Api()
    cm = client.read_namespaced_config_map(name=name, namespace=namespace)

    rc = {}
    for item in rcs:
        rc[item] = cm.data.get(item.upper(), getattr(settings, item, None))

    app.rest_configs[name] = rc


@router.get("/")
async def config_list():
    from main import app

    return app.rest_configs


@router.get("/default/refresh/")
async def config_default_refresh():
    default_rest_config = await config_refresh(name=settings.cc_default_name)
    return default_rest_config


@router.get("/{config_name}/refresh/")
async def config_refresh(config_name: str):
    from main import app

    try:
        update_cluster_config(name=config_name)
    except Exception:
        raise HTTPException(status_code=500, detail="Rest configmap error")

    return app.rest_configs
