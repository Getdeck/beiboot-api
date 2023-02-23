import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("uvicorn.beiboot")

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/headers")
async def get_headers(request: Request):
    # user headers
    x_forwarded_user = request.headers.get("X-Forwarded-User", None)
    x_forwarded_groups = request.headers.get("X-Forwarded-Groups", None)
    x_forwarded_email = request.headers.get("X-Forwarded-Email", None)
    x_forwarded_preferred_username = request.headers.get("X-Forwarded-Preferred-Username", None)

    response = JSONResponse(
        content={
            "X-Forwarded-User": x_forwarded_user,
            "X-Forwarded-Groups": x_forwarded_groups,
            "X-Forwarded-Email": x_forwarded_email,
            "X-Forwarded-Preferred-Username": x_forwarded_preferred_username,
        }
    )
    return response


@router.get("/sentry")
async def trigger_error():
    _ = 1 / 0
