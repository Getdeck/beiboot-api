import logging
from typing import Annotated, List

from cluster.service import ClusterService, get_cluster_service
from cluster.types import Labels
from exceptions import BeibootException
from fastapi import APIRouter, Depends, HTTPException, Request, status
from headers import user_headers
from pydantic import BaseModel

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/connections", tags=["connections"], dependencies=[Depends(user_headers)])


class GhostunnelPort(BaseModel):
    endpoint: str
    target: int


class GhostunnelResponse(BaseModel):
    mtls: dict
    ports: List[GhostunnelPort] | None


@router.get("/{cluster_id}/ghostunnel/", response_model=GhostunnelResponse)
async def ghostunnel(
    request: Request, cluster_id: str, handler: Annotated[ClusterService, Depends(get_cluster_service)]
):
    try:
        labels = Labels(user=request.state.user)
        beiboot = handler.get(cluster_id=cluster_id, labels=labels)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    if not beiboot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found.")

    if not beiboot.mtls_files or not beiboot.tunnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection files not available.")

    response = GhostunnelResponse(mtls=beiboot.mtls_files, ports=beiboot.tunnel["ghostunnel"]["ports"])
    return response
