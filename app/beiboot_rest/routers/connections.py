import logging

from beiboot import api
from exceptions import BeibootException
from fastapi import APIRouter, Depends
from headers import user_headers
from pydantic import BaseModel

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/connections", tags=["connections"], dependencies=[Depends(user_headers)])


class GhostTunnelResponse(BaseModel):
    mtls: dict


@router.get("/{cluster_name}/ghost-tunnel/", response_model=GhostTunnelResponse)
async def ghost_tunnel(cluster_name):
    try:
        beiboot = api.read(name=cluster_name)
    except Exception as e:
        raise BeibootException(message="Beiboot Error", error=str(e))

    response = GhostTunnelResponse(mtls=beiboot.mtls_files)
    return response
