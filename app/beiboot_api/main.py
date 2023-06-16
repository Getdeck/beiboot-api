import logging

import kubernetes as k8s
from exceptions import BeibootException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from group.helper import group_filter_and_selection
from routers import clusters, configs, connections, debug
from sentry import sentry_setup
from sentry_sdk import capture_exception
from settings import get_settings

logger = logging.getLogger("uvicorn.beiboot")


app = FastAPI()


@app.middleware("http")
async def user_middleware(request: Request, call_next):
    settings = get_settings()  # TODO: optimize group service settings

    # user
    request.state.user = request.headers.get("X-Forwarded-User", None)

    # groups
    x_forwarded_groups = request.headers.get("X-Forwarded-Groups", None)
    groups_filtered, group_selected = group_filter_and_selection(
        x_forwarded_groups=x_forwarded_groups, settings=settings
    )
    request.state.groups = groups_filtered
    request.state.group_selected = group_selected

    response = await call_next(request)
    return response


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
