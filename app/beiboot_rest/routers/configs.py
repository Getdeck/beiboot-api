import kubernetes as k8s
from config import settings
from fastapi import APIRouter

router = APIRouter(prefix="/configs", tags=["configs"])

rcs = [
    "rc_cluster_lifetime_limit",
    "rc_cluster_node_limit",
]


def update_beiboot_rest_config(name: str = settings.rc_default_name, namespace: str = settings.rc_default_namespace):
    from main import app

    client = k8s.client.CoreV1Api()
    cm = client.read_namespaced_config_map(name=name, namespace=namespace)

    rc = {}
    for item in rcs:
        rc[item] = cm.data.get(item.upper(), getattr(settings, item, None))

    app.rest_configs[name] = rc  # type: ignore


@router.get("/")
async def config_list():
    from main import app

    return app.rest_configs  # type: ignore


@router.get("/default/refresh/")
async def config_default_refresh():
    default_rest_config = await config_refresh(name=settings.rc_default_name)
    return default_rest_config


@router.get("/{name}/refresh/")
async def config_refresh(name: str):
    from main import app

    update_beiboot_rest_config(name=name)
    return app.rest_configs  # type: ignore
