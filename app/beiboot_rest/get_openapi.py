from fastapi.openapi.utils import get_openapi
from beiboot_rest import main
import json

print(get_openapi(
    title=main.app.title,
    version=main.app.version,
    openapi_version=main.app.openapi_version,
    description=main.app.description,
    routes=main.app.routes,
    ))
