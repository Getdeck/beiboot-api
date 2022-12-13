import logging

import sentry_sdk

logger = logging.getLogger()


def sentry_setup(dsn: str, environment: str):
    if not dsn:
        return

    try:
        with open("version.txt", "r") as file:
            release = file.read().rstrip()
    except Exception as e:
        logger.error(str(e))
        release = "unknown"

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
    )
