import logging
from importlib import metadata

import sentry_sdk

logger = logging.getLogger()


def sentry_setup(dsn: str, environment: str):
    if not dsn:
        return

    release = metadata.version("beiboot_rest")

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
    )
