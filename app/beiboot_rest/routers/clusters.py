from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from beiboot_rest.type import ClusterData
from beiboot import api
from beiboot.types import BeibootRequest, BeibootParameters

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("/")
async def cluster_list():
    return {}


@router.post("/")
async def cluster_create(data: ClusterData):
    req = BeibootRequest(
        name=data.name,
        parameters=BeibootParameters(
            nodes=1,
            serverStorageRequests="500Mi",
            serverResources={"requests": {"cpu": "0.25", "memory": "0.25Gi"}},
            nodeResources={"requests": {"cpu": "0.25", "memory": "0.25Gi"}},
        ),
    )
    beiboot = api.create(req=req)
    response = JSONResponse(content={"state": str(beiboot.state)})
    return response


@router.delete("/{uuid}")
async def cluster_delete(uuid: UUID):
    response = JSONResponse(content={})
    return response
