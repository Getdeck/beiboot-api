import asyncio
import logging
from datetime import datetime
from io import BytesIO
from typing import List

from beiboot import api
from beiboot.types import BeibootParameters, BeibootProvider, BeibootRequest
from cluster.types import (
    ClusterInfoResponse,
    ClusterParameter,
    ClusterRequest,
    ClusterStateResponse,
    IntegerParameter,
    Parameters,
)
from cluster_config.types import ClusterConfig
from config import settings
from exceptions import BeibootException
from fastapi import APIRouter, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect, status
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


@router.get("/ws/{cluster_name}")
async def get(cluster_name: str):
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>WebSocket</title>
            </head>
            <body>
                <h1>WebSocket</h1>
                <script>
                    var ws = new WebSocket(`ws://localhost:8000/clusters/{cluster_name}/heartbeat`);
                </script>
            </body>
        </html>
        """
    )


@router.get("/", response_model=Page[ClusterStateResponse])
async def cluster_list(params: Params = Depends()) -> List[ClusterStateResponse]:
    try:
        beiboots = api.read_all()
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = []
    for beiboot in beiboots:
        response.append(ClusterStateResponse(name=beiboot.name, state=beiboot.state))

    return paginate(response, params)


@router.get("/{cluster_name}", response_model=ClusterInfoResponse)
async def cluster_info(cluster_name: str) -> ClusterInfoResponse:
    try:
        beiboot = api.read(name=cluster_name)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = ClusterInfoResponse(
        name=beiboot.name,
        namespace=beiboot.namespace,
        state=beiboot.state,
        parameters=[
            IntegerParameter(
                name=ClusterParameter.NODE_COUNT.value,
                value=beiboot.parameters.nodes,
            )
        ],
    )
    return response


@router.post("/", response_model=ClusterStateResponse)
async def cluster_create(request: ClusterRequest) -> ClusterStateResponse:
    name = request.name

    # parameter validation via pydantic
    cluster_config = ClusterConfig(**settings.dict())
    tmp = {str(parameter.name.value): parameter for parameter in request.parameters}

    try:
        parameters = Parameters(cluster_config=cluster_config, **tmp)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())

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
    try:
        beiboot = api.create(req=req)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = ClusterStateResponse(name=beiboot.name, state=beiboot.state)
    return response


@router.delete("/{cluster_name}")
async def cluster_delete(cluster_name: str) -> None:
    try:
        api.delete_by_name(name=cluster_name)
    except RuntimeWarning as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/{cluster_name}/heartbeat", response_model=ClusterStateResponse)
async def cluster_state(request: Request, cluster_name: str) -> ClusterStateResponse:
    x_forwarded_user = request.headers.get("X-Forwarded-User")

    try:
        beiboot = api.read(name=cluster_name)
        _ = api.write_heartbeat(
            client_id=x_forwarded_user,
            bbt=beiboot,
        )
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = ClusterStateResponse(name=beiboot.name, state=beiboot.state)
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
    try:
        beiboot = api.read(name=cluster_name)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    kubeconfig = BytesIO(beiboot.kubeconfig.encode())
    return StreamingResponse(kubeconfig, media_type="application/yaml")


@router.get("/{cluster_name}/parameters", response_model=Page[dict])
async def cluster_parameters(cluster_name: str, params: Params = Depends()):
    response = []
    return paginate(response, params)


@router.get("/{cluster_name}/parameters/{parameter_name}")
async def cluster_parameter(cluster_name: str, parameter_name: str):
    pass
