import logging

import sentry_sdk

logger = logging.getLogger("uvicorn.beiboot")


def sentry_setup(dsn: str, environment: str) -> None:
    if not dsn:
        return None

    try:
        with open("version.txt") as file:
            release = file.read()
    except Exception:
        release = "unknown"

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
    )

    logger.info(f"Sentry setup: {dsn or '-'} ({environment or '-'}).")
