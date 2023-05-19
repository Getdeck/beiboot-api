import logging
from typing import Annotated

import kubernetes as k8s
import timeout_decorator
from config.types import Config
from fastapi import Depends
from kubernetes.client.rest import ApiException
from settings import Settings, get_settings

logger = logging.getLogger("uvicorn.beiboot")


class ConfigService:
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings

    # @timeout_decorator.timeout(5, timeout_exception=Exception)
    def get(
        self,
        prefix: str | None = None,
        name: str | None = None,
        namespace: str | None = None,
    ) -> Config:
        if not prefix:
            prefix = self.settings.config_prefix

        if not name:
            name = self.settings.config_default_name

        if not namespace:
            namespace = self.settings.config_default_namespace

        config_map_name = f"{prefix}{name}"

        try:
            client = k8s.client.CoreV1Api()
            cm = client.read_namespaced_config_map(name=config_map_name, namespace=namespace)
        except ApiException as e:
            logger.error(e)
            raise ValueError(f"ConfigMap {name} not found in namespace {namespace}")

        cc = {}
        for item in Config.__fields__:
            cc[item] = cm.data.get(item.upper(), getattr(self.settings, item, None))

        return Config(**cc)


def get_cluster_config_service(service: Annotated[ConfigService, Depends(ConfigService)]) -> ConfigService:
    return service
