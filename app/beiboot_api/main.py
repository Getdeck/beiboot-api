import logging

import kubernetes as k8s
from exceptions import BeibootException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import clusters, configs, connections, debug
from sentry import sentry_setup
from sentry_sdk import capture_exception
from settings import get_settings

logger = logging.getLogger("uvicorn.beiboot")


app = FastAPI()


from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource(attributes={SERVICE_NAME: "getdeck-api"})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4327"))
# processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Merrily go about tracing!

tracer = trace.get_tracer("my.tracer.name")


@app.middleware("http")
async def user_middleware(request: Request, call_next):
    request.state.user = request.headers.get("X-Forwarded-User", None)

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
    with tracer.start_as_current_span("span-name"):
        # do some work that 'span' will track
        print("doing some work...")
        # When the 'with' block goes out of scope, 'span' is closed for you
    return {"Beiboot": "API"}


app.include_router(clusters.router)
app.include_router(connections.router)
app.include_router(configs.router)
app.include_router(debug.router)
