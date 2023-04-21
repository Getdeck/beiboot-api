import logging
from typing import List

from beiboot import api
from exceptions import BeibootException
from fastapi import APIRouter, Depends
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


@router.get("/{cluster_name}/ghostunnel/", response_model=GhostunnelResponse)
async def ghostunnel(cluster_name):
    try:
        beiboot = api.read(name=cluster_name)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = GhostunnelResponse(mtls=beiboot.mtls_files, ports=beiboot.tunnel["ghostunnel"]["ports"])
    return response
