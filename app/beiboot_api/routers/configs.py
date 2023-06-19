import logging
from typing import Annotated

from config.service import ConfigService, get_cluster_config_service
from config.types import ConfigInfoResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from group.service import GroupService, get_group_service
from headers import user_headers
from settings import Settings, get_settings

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/configs", tags=["configs"], dependencies=[Depends(user_headers)])


@router.get("/selected/")
async def config_selected(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
    config_service: Annotated[ConfigService, Depends(get_cluster_config_service)],
) -> ConfigInfoResponse:
    group_selected = group_service.select(x_forwarded_groups=request.headers.get("x-forwarded-groups"))

    for name in [group_selected, settings.config_default_name]:
        try:
            response = await config_custom(request=request, name=name, settings=settings, config_service=config_service)
            return response
        except Exception:
            pass
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/default/")
async def config_default(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    config_service: Annotated[ConfigService, Depends(get_cluster_config_service)],
) -> ConfigInfoResponse:
    response = await config_custom(
        request=request, name=settings.config_default_name, settings=settings, config_service=config_service
    )
    return response


@router.get("/{name}/")
async def config_custom(
    request: Request,
    name: str,
    settings: Annotated[Settings, Depends(get_settings)],
    config_service: Annotated[ConfigService, Depends(get_cluster_config_service)],
):
    if name not in request.state.groups and name != settings.config_default_name:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        cc = config_service.get(prefix=settings.config_prefix, name=name, namespace=settings.config_default_namespace)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = ConfigInfoResponse(
        default=False,
        name=name,
        config=cc,
    )
    return response
