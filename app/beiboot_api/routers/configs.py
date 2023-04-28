import logging
from typing import Annotated

from config.service import ConfigService, get_cluster_config_service
from config.types import ConfigInfoResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from headers import user_headers
from settings import Settings, get_settings

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/configs", tags=["configs"], dependencies=[Depends(user_headers)])


@router.get("/default/")
async def config_default(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    handler: Annotated[ConfigService, Depends(get_cluster_config_service)],
) -> ConfigInfoResponse:
    cc = await config_custom(
        request=request, config_name=settings.config_default_name, settings=settings, handler=handler
    )

    response = ConfigInfoResponse(
        default=True,
        name="default",
        config=cc,
    )
    return response


@router.get("/{config_name}/")
async def config_custom(
    request: Request,
    config_name: str,
    settings: Annotated[Settings, Depends(get_settings)],
    handler: Annotated[ConfigService, Depends(get_cluster_config_service)],
):
    if config_name not in request.state.groups and config_name != settings.config_default_name:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        cc = handler.get(prefix=settings.config_prefix, name=config_name, namespace=settings.config_default_namespace)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = ConfigInfoResponse(
        default=False,
        name=config_name,
        config=cc,
    )
    return response
