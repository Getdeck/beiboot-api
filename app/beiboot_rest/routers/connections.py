import logging

from beiboot import api
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from headers import user_headers

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/connections", tags=["connections"], dependencies=[Depends(user_headers)])


@router.get("/{cluster_name}/ghost-tunnel/")
async def ghost_tunnel(cluster_name):
    beiboot = api.read(name=cluster_name)
    response = JSONResponse(content=beiboot.mtls_files)
    return response
