import asyncio
import logging
from datetime import datetime
from io import BytesIO
from typing import List

from beiboot import api
from beiboot.types import BeibootParameters, BeibootProvider, BeibootRequest
from cluster.types import ClusterRequest, ClusterResponse, Parameters
from cluster_config.types import ClusterConfig
from config import settings
from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi_pagination import Page, Params, paginate
from headers import user_headers

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/clusters", tags=["clusters"], dependencies=[Depends(user_headers)])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


manager = ConnectionManager()


@router.get("/ws")
async def get():
    cluster_name = "test"
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Heartbeat</title>
            </head>
            <body>
                <h1>WebSocket Heartbeat</h1>
                <script>
                    var ws = new WebSocket(`ws://localhost:8001/clusters/{cluster_name}/heartbeat`);
                </script>
            </body>
        </html>
        """
    )


@router.get("/", response_model=Page[ClusterResponse])
async def cluster_list(params: Params = Depends()) -> List[ClusterResponse]:
    beiboots = api.read_all()

    response = []
    for beiboot in beiboots:
        response.append(ClusterResponse(name=beiboot.name, state=beiboot.state))

    return paginate(response, params)


@router.get("/{cluster_name}", response_model=ClusterResponse)
async def cluster_info(cluster_name: str) -> ClusterResponse:
    beiboot = api.read(name=cluster_name)
    response = ClusterResponse(name=beiboot.name, state=beiboot.state)
    return response


@router.post("/", response_model=ClusterResponse)
async def cluster_create(request: ClusterRequest) -> ClusterResponse:
    name = request.name

    # parameter validation via pydantic
    cluster_config = ClusterConfig(**settings.dict())
    tmp = {str(parameter.name.value): parameter for parameter in request.parameters}

    try:
        parameters = Parameters(cluster_config=cluster_config, **tmp)
    except Exception as e:
        # TODO: error response
        raise e

    # cluster creation
    req = BeibootRequest(
        name=name,
        provider=BeibootProvider.K3S,
        parameters=BeibootParameters(
            k8sVersion=parameters.k8s_version.value,
            nodes=parameters.node_count.value,
            maxLifetime=parameters.lifetime.value,
            maxSessionTimeout=parameters.session_timeout.value,
        ),
    )
    beiboot = api.create(req=req)

    response = ClusterResponse(name=beiboot.name, state=beiboot.state)
    return response


@router.delete("/{cluster_name}", response_model=ClusterResponse)
async def cluster_delete(cluster_name: str) -> ClusterResponse:
    api.delete_by_name(name=cluster_name)
    return ClusterResponse(name=cluster_name, state=None)


@router.get("/{cluster_name}/heartbeat", response_model=ClusterResponse)
async def cluster_state(request: Request, cluster_name: str) -> ClusterResponse:
    x_forwarded_user = request.headers.get("X-Forwarded-User")

    beiboot = api.read(name=cluster_name)
    _ = api.write_heartbeat(
        client_id=x_forwarded_user,
        bbt=beiboot,
    )

    response = ClusterResponse(name=beiboot.name, state=beiboot.state)
    return response


@router.websocket("/{cluster_name}/heartbeat")
async def websocket_endpoint(websocket: WebSocket, cluster_name: str):
    x_forwarded_user = websocket.headers.get("X-Forwarded-User") or "unknown"

    await manager.connect(websocket)
    logger.info(
        f"{datetime.now().isoformat()} - Websocket connection opened (cluster: '{cluster_name}', client: '{x_forwarded_user}')."
    )

    try:
        beiboot = api.read(name=cluster_name)
    except RuntimeError:
        manager.disconnect(websocket)
        raise Exception("Invalid 'cluster_name'.")

    try:
        while True:
            # probe websocket connection
            try:
                _ = await asyncio.wait_for(websocket.receive_text(), 5)
            except asyncio.TimeoutError:
                pass

            # write heartbeat
            _ = api.write_heartbeat(
                client_id=x_forwarded_user,
                bbt=beiboot,
            )
            logger.debug(
                f"{datetime.now().isoformat()} - Websocket <3 (cluster: '{cluster_name}', client: '{x_forwarded_user}')."
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(
            f"{datetime.now().isoformat()} - Websocket connection closed (cluster: '{cluster_name}', client: '{x_forwarded_user}')."
        )


@router.get("/{cluster_name}/kubeconfig")
async def cluster_kubeconfig(cluster_name: str):
    beiboot = api.read(name=cluster_name)
    kubeconfig = BytesIO(beiboot.kubeconfig.encode())
    return StreamingResponse(kubeconfig, media_type="application/yaml")


@router.get("/{cluster_name}/parameters", response_model=Page[dict])
async def cluster_parameters(cluster_name: str, params: Params = Depends()):
    response = []
    return paginate(response, params)


@router.get("/{cluster_name}/parameters/{parameter_name}")
async def cluster_parameter(cluster_name: str, parameter_name: str):
    pass
