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
    ClusterReadyTimeout,
    ClusterRequest,
    ClusterStateResponse,
    GefyraEnabled,
    GefyraEndpoint,
    K8sVersion,
    Labels,
    Lifetime,
    NodeCount,
    NodeResourcesLimitsCpu,
    NodeResourcesLimitsMemory,
    NodeResourcesRequestsCpu,
    NodeResourcesRequestsMemory,
    NodeStorageRequests,
    Ports,
    ServerResourcesLimitsCpu,
    ServerResourcesLimitsMemory,
    ServerResourcesRequestsCpu,
    ServerResourcesRequestsMemory,
    ServerStorageRequests,
    SessionTimeout,
    TunnelEnabled,
    TunnelEndpoint,
)
from exceptions import BeibootException
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi_pagination import Page, Params, paginate
from group.service import GroupService, get_group_service
from headers import user_headers
from settings import Settings, get_settings

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
    request: Request,
    cluster_service: Annotated[ClusterService, Depends(get_cluster_service)],
    params: Params = Depends(),
) -> List[ClusterStateResponse]:
    try:
        labels = Labels(user=request.state.user)
        beiboots = cluster_service.list(labels=labels)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = []
    for beiboot in beiboots:
        response.append(ClusterStateResponse(id=beiboot.name, name=beiboot.labels.get("name"), state=beiboot.state))

    return paginate(response, params)


@router.get("/{cluster_id}", response_model=ClusterInfoResponse)
async def cluster_info(
    request: Request, cluster_id: str, cluster_service: Annotated[ClusterService, Depends(get_cluster_service)]
) -> ClusterInfoResponse:
    try:
        labels = Labels(user=request.state.user)
        beiboot = cluster_service.get(cluster_id=cluster_id, labels=labels)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    if not beiboot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found.")

    # parameters
    parameters = [
        K8sVersion(value=beiboot.parameters.k8sVersion),
        Ports(value=beiboot.parameters.ports),
        NodeCount(value=beiboot.parameters.nodes),
        Lifetime(value=beiboot.parameters.maxLifetime),
        SessionTimeout(value=beiboot.parameters.maxSessionTimeout),
        ClusterReadyTimeout(value=beiboot.parameters.clusterReadyTimeout),
        ServerResourcesRequestsCpu(value=beiboot.parameters.serverResources.get("requests", {}).get("cpu")),
        ServerResourcesRequestsMemory(value=beiboot.parameters.serverResources.get("requests", {}).get("memory")),
        ServerResourcesLimitsCpu(value=beiboot.parameters.serverResources.get("limits", {}).get("cpu")),
        ServerResourcesLimitsMemory(value=beiboot.parameters.serverResources.get("limits", {}).get("memory")),
        ServerStorageRequests(value=beiboot.parameters.serverStorageRequests),
        NodeResourcesRequestsCpu(value=beiboot.parameters.nodeResources.get("requests", {}).get("cpu")),
        NodeResourcesRequestsMemory(value=beiboot.parameters.nodeResources.get("requests", {}).get("memory")),
        NodeResourcesLimitsCpu(value=beiboot.parameters.nodeResources.get("limits", {}).get("cpu")),
        NodeResourcesLimitsMemory(value=beiboot.parameters.nodeResources.get("limits", {}).get("memory")),
        NodeStorageRequests(value=beiboot.parameters.nodeStorageRequests),
        GefyraEnabled(value=beiboot.parameters.gefyra.get("enabled")),
        GefyraEndpoint(value=beiboot.parameters.gefyra.get("endpoint")),
        TunnelEnabled(value=beiboot.parameters.tunnel.get("enabled")),
        TunnelEndpoint(value=beiboot.parameters.tunnel.get("endpoint")),
    ]

    # filter parameters with empty values
    parameters_filtered = [parameter for parameter in parameters if parameter.value is not None]

    if beiboot.sunset:
        sunset = datetime.strptime(beiboot.sunset, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        sunset = None

    response = ClusterInfoResponse(
        id=beiboot.name,
        name=beiboot.labels.get("name"),
        namespace=beiboot.namespace,
        state=beiboot.state,
        sunset=sunset,
        parameters=parameters_filtered,
    )
    return response


@router.post("/", response_model=ClusterStateResponse)
async def cluster_create(  # noqa: C901
    request: Request,
    group_service: Annotated[GroupService, Depends(get_group_service)],
    cluster_service: Annotated[ClusterService, Depends(get_cluster_service)],
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
    # validate group: TODO: move to ClusterRequest validator?
    if not cluster_request.group:
        group_selected = group_service.select(x_forwarded_groups=request.headers.get("x-forwarded-groups"))
        cluster_request.group = group_selected

    available_groups = group_service.available_groups()
    if cluster_request.group not in available_groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid group: {cluster_request.group}. Available groups: {available_groups.join(', ')}.",
        )

    # validate group cluster limit
    try:
        labels = Labels(group=cluster_request.group)
        beiboots = cluster_service.list(labels=labels)
        beiboot_group_count = len(beiboots)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    group_config = group_service.get_config(name=cluster_request.group)
    if not group_config.group_cluster_limit:
        pass  # no group limit -> skip validation
    else:
        if beiboot_group_count >= group_config.group_cluster_limit:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Group cluster limit reached.")

    # validate user cluster limit
    try:
        labels = Labels(user=request.state.user)
        beiboots = cluster_service.list(labels=labels)
        beiboot_user_count = len(beiboots)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    if beiboot_user_count >= group_config.user_cluster_limit:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="User cluster limit reached.")

    # create cluster
    try:
        beiboot = cluster_service.create(request=request, cluster_request=cluster_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = ClusterStateResponse(id=beiboot.name, name=beiboot.labels.get("name"), state=beiboot.state)
    return response


@router.delete("/{cluster_id}")
async def cluster_delete(
    request: Request, cluster_id: str, cluster_service: Annotated[ClusterService, Depends(get_cluster_service)]
) -> None:
    try:
        labels = Labels(user=request.state.user)
        cluster_service.delete(cluster_id=cluster_id, labels=labels)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cluster id unknown")
    except RuntimeWarning as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/{cluster_id}/heartbeat", response_model=ClusterStateResponse)
async def cluster_heartbeat(
    request: Request, cluster_id: str, cluster_service: Annotated[ClusterService, Depends(get_cluster_service)]
) -> ClusterStateResponse:
    try:
        beiboot = cluster_service.get(cluster_id=cluster_id)
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
    websocket: WebSocket, cluster_id: str, cluster_service: Annotated[ClusterService, Depends(get_cluster_service)]
):
    x_forwarded_user = websocket.headers.get("X-Forwarded-User") or "unknown"

    await manager.connect(websocket)
    logger.info(
        f"{datetime.now().isoformat()} - Websocket connection opened (cluster: '{cluster_id}', client: '{x_forwarded_user}')."
    )

    try:
        labels = Labels(user=websocket.state.user)
        beiboot = cluster_service.get(cluster_id=cluster_id, labels=labels)
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
    request: Request, cluster_id: str, cluster_service: Annotated[ClusterService, Depends(get_cluster_service)]
):
    try:
        labels = Labels(user=request.state.user)
        beiboot = cluster_service.get(cluster_id=cluster_id, labels=labels)
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
