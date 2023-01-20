from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from beiboot import api
from beiboot.types import BeibootRequest
from typing import List

from beiboot_rest.type import BeibootRequest, BeibootResponse
from fastapi.responses import JSONResponse

from beiboot import api
from beiboot import types as bbt_dataclass


def user_headers(user_id: str | None = Header(default="default")):
    return {"user_id": user_id}


router = APIRouter(prefix="/clusters", tags=["clusters"], dependencies=[Depends(user_headers)])


@router.get("/", response_model=List[BeibootResponse])
async def cluster_list(request: Request) -> List[BeibootResponse]:
    beiboots = api.read_all()

    response = []
    for beiboot in beiboots:
        response.append(BeibootResponse(name=beiboot.name, state=beiboot.state))
    return response


@router.post("/", response_model=BeibootResponse)
async def cluster_create(beiboot_request: BeibootRequest) -> BeibootResponse:
    req = bbt_dataclass.BeibootRequest(
        name=beiboot_request.name,
        provider=bbt_dataclass.BeibootProvider(beiboot_request.provider),
        parameters=bbt_dataclass.BeibootParameters(**beiboot_request.parameters.dict()),
        labels=beiboot_request.labels,
    )

    beiboot = api.create(req=req)
    response = BeibootResponse(name=beiboot.name, state=beiboot.state)
    return response


@router.delete("/{name}", response_model=BeibootResponse)
async def cluster_delete(name: str) -> BeibootResponse:
    api.delete_by_name(name=name)
    return JSONResponse(content={})


@router.get("/{name}/state", response_model=BeibootResponse)
async def cluster_state(name: str) -> BeibootResponse:
    beiboot = api.read(name=name)
    response = BeibootResponse(name=beiboot.name, state=beiboot.state)
    return response


@router.get("/{name}/kubeconfig")
async def cluster_kubeconfig(name: str):
    beiboot = api.read(name=name)
    response = JSONResponse(content={"kubeconfig": beiboot.kubeconfig})
    return response


@router.get("/{name}/mtls")
async def cluster_mtls(name: str):
    beiboot = api.read(name=name)
    response = JSONResponse(content=beiboot.mtls_files)
    return response
