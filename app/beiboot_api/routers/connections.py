import logging
from typing import List

from beiboot import api
from cluster.types import Labels
from exceptions import BeibootException
from fastapi import APIRouter, Depends, HTTPException, Request, status
from headers import user_headers
from pydantic import BaseModel
from routers.clusters import validate_cluster_name

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/connections", tags=["connections"], dependencies=[Depends(user_headers)])


class GhostunnelPort(BaseModel):
    endpoint: str
    target: int


class GhostunnelResponse(BaseModel):
    mtls: dict
    ports: List[GhostunnelPort] | None


@router.get("/{cluster_name}/ghostunnel/", response_model=GhostunnelResponse)
async def ghostunnel(request: Request, cluster_name: str):
    labels = Labels(user=request.headers.get("X-Forwarded-User"))

    if not validate_cluster_name(labels=labels, cluster_name=cluster_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cluster not found")

    try:
        beiboot = api.read(name=cluster_name)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = GhostunnelResponse(mtls=beiboot.mtls_files, ports=beiboot.tunnel["ghostunnel"]["ports"])
    return response
