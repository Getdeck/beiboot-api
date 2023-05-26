import asyncio
import logging
from datetime import datetime
from io import BytesIO
from typing import Annotated, List

from beiboot import api
from cluster.service import ClusterService, get_cluster_service
from cluster.types import (
    ClusterInfoResponse,
    ClusterParameter,
    ClusterRequest,
    ClusterStateResponse,
    K8sVersion,
    Labels,
    Lifetime,
    NodeCount,
    Ports,
    SessionTimeout,
)
from exceptions import BeibootException
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect, status
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


@router.get("/", response_model=Page[ClusterStateResponse])
async def cluster_list(
    request: Request, handler: Annotated[ClusterService, Depends(get_cluster_service)], params: Params = Depends()
) -> List[ClusterStateResponse]:
    try:
        labels = Labels(user=request.state.user)
        beiboots = handler.list(labels=labels)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = []
    for beiboot in beiboots:
        response.append(ClusterStateResponse(id=beiboot.name, name=beiboot.labels.get("name"), state=beiboot.state))

    return paginate(response, params)


@router.get("/{cluster_id}", response_model=ClusterInfoResponse)
async def cluster_info(
    request: Request, cluster_id: str, handler: Annotated[ClusterService, Depends(get_cluster_service)]
) -> ClusterInfoResponse:
    try:
        labels = Labels(user=request.state.user)
        beiboot = handler.get(cluster_id=cluster_id, labels=labels)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    if not beiboot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found.")

    response = ClusterInfoResponse(
        id=beiboot.name,
        name=beiboot.labels.get("name"),
        namespace=beiboot.namespace,
        state=beiboot.state,
        parameters=[
            K8sVersion(value=beiboot.parameters.k8sVersion),
            Ports(value=beiboot.parameters.ports),
            NodeCount(value=beiboot.parameters.nodes),
            Lifetime(value=beiboot.parameters.maxLifetime),
            SessionTimeout(value=beiboot.parameters.maxSessionTimeout),
        ],
    )
    return response


@router.post("/", response_model=ClusterStateResponse)
async def cluster_create(
    request: Request,
    handler: Annotated[ClusterService, Depends(get_cluster_service)],
    cluster_request: ClusterRequest = Body(
        example={
            "name": "hello",
            "parameters": [
                {
                    "name": ClusterParameter.K8S_VERSION.value,
                    "value": "1.26.0",
                },
                {
                    "name": ClusterParameter.PORTS.value,
                    "value": ["80:80", "443:443"],
                },
                {
                    "name": ClusterParameter.NODE_COUNT.value,
                    "value": 1,
                },
                {
                    "name": ClusterParameter.LIFETIME.value,
                    "value": "1h",
                },
                {
                    "name": ClusterParameter.SESSION_TIMEOUT.value,
                    "value": "5m",
                },
            ],
        },
    ),
) -> ClusterStateResponse:
    try:
        beiboot = handler.create(request=request, cluster_request=cluster_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = ClusterStateResponse(id=beiboot.name, name=beiboot.labels.get("name"), state=beiboot.state)
    return response


@router.delete("/{cluster_id}")
async def cluster_delete(
    request: Request, cluster_id: str, handler: Annotated[ClusterService, Depends(get_cluster_service)]
) -> None:
    try:
        labels = Labels(user=request.state.user)
        handler.delete(cluster_id=cluster_id, labels=labels)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cluster id unknown")
    except RuntimeWarning as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/{cluster_id}/heartbeat", response_model=ClusterStateResponse)
async def cluster_heartbeat(
    request: Request, cluster_id: str, handler: Annotated[ClusterService, Depends(get_cluster_service)]
) -> ClusterStateResponse:
    try:
        beiboot = handler.get(cluster_id=cluster_id)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    if not beiboot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found.")

    _ = api.write_heartbeat(
        client_id=request.state.user,
        bbt=beiboot,
    )

    response = ClusterStateResponse(id=beiboot.name, name=beiboot.labels.get("name"), state=beiboot.state)
    return response


@router.websocket("/{cluster_id}/heartbeat")
async def websocket_endpoint(
    websocket: WebSocket, cluster_id: str, handler: Annotated[ClusterService, Depends(get_cluster_service)]
):
    x_forwarded_user = websocket.headers.get("X-Forwarded-User") or "unknown"

    await manager.connect(websocket)
    logger.info(
        f"{datetime.now().isoformat()} - Websocket connection opened (cluster: '{cluster_id}', client: '{x_forwarded_user}')."
    )

    try:
        labels = Labels(user=websocket.state.user)
        beiboot = handler.get(cluster_id=cluster_id, labels=labels)
    except RuntimeError:
        manager.disconnect(websocket)
        raise Exception("Invalid 'cluster_id'.")

    if not beiboot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found.")

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
                f"{datetime.now().isoformat()} - Websocket <3 (cluster: '{cluster_id}', client: '{x_forwarded_user}')."
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(
            f"{datetime.now().isoformat()} - Websocket connection closed (cluster: '{cluster_id}', client: '{x_forwarded_user}')."
        )


@router.get("/{cluster_id}/kubeconfig")
async def cluster_kubeconfig(
    request: Request, cluster_id: str, handler: Annotated[ClusterService, Depends(get_cluster_service)]
):
    try:
        labels = Labels(user=request.state.user)
        beiboot = handler.get(cluster_id=cluster_id, labels=labels)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    if not beiboot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found.")

    if not beiboot.kubeconfig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kubeconfig not available.")

    kubeconfig = BytesIO(beiboot.kubeconfig.encode())
    return StreamingResponse(kubeconfig, media_type="application/yaml")


# @router.get("/{cluster_id}/parameters", response_model=Page[dict])
# async def cluster_parameters(cluster_id: str, params: Params = Depends()):
#     response = []
#     return paginate(response, params)


# @router.get("/{cluster_id}/parameters/{parameter_name}")
# async def cluster_parameter(cluster_id: str, parameter_name: str):
#     pass


@router.get("/ws/{cluster_id}")
async def get(cluster_id: str):
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
                    var ws = new WebSocket(`ws://localhost:8000/clusters/{cluster_id}/heartbeat`);
                </script>
            </body>
        </html>
        """
    )
