from fastapi.openapi.utils import get_openapi
import main
import json

with open("openapi.json", "w") as f:
    json.dump(get_openapi(
        title=main.app.title,
        version=main.app.version,
        openapi_version=main.app.openapi_version,
        description=main.app.description,
        routes=main.app.routes,
        ), f)
