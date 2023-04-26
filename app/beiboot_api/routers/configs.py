import logging
from typing import Annotated

import kubernetes as k8s
import timeout_decorator
from cluster_config.types import ClusterConfig
from config import Settings, get_settings
from fastapi import APIRouter, Depends, HTTPException
from headers import user_headers

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/configs", tags=["configs"], dependencies=[Depends(user_headers)])


@timeout_decorator.timeout(5, timeout_exception=Exception)
def update_cluster_config(
    settings: Annotated[Settings, Depends(get_settings)],
    name: str | None = None,
    namespace: str | None = None,
):
    from main import app

    if not name:
        name = settings.cc_default_name

    if not namespace:
        namespace = settings.cc_default_namespace

    client = k8s.client.CoreV1Api()
    cm = client.read_namespaced_config_map(name=name, namespace=namespace)

    cc = {}
    for item in ClusterConfig.__fields__:
        cc[item] = cm.data.get(item.upper(), getattr(settings, item, None))

    app.cluster_configs[name] = cc


@router.get("/")
async def config_list():
    from main import app

    return app.cluster_configs


@router.get("/default/refresh/")
async def config_default_refresh(settings: Annotated[Settings, Depends(get_settings)]):
    default_api_config = await config_refresh(name=settings.cc_default_name)
    return default_api_config


@router.get("/{config_name}/refresh/")
async def config_refresh(config_name: str):
    from main import app

    try:
        update_cluster_config(name=config_name)
    except Exception:
        raise HTTPException(status_code=500, detail="API configmap error")

    return app.cluster_configs
