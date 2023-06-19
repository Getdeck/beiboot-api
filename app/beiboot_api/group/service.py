import logging
from typing import Annotated, List, Union

import kubernetes as k8s
import timeout_decorator
from fastapi import Depends
from group.types import GroupConfig
from kubernetes.client.rest import ApiException
from settings import Settings, get_settings

logger = logging.getLogger("uvicorn.beiboot")


class GroupService:
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings

    def available_groups(self) -> Union[List[str], str]:
        return ["developer", "free", self.settings.group_default_name]  # TODO: fixed set of groups currently

    def _parse_group_header(self, x_forwarded_groups: str | None) -> List[str]:
        if not x_forwarded_groups:
            return []

        if type(x_forwarded_groups) == str:
            x_forwarded_groups = x_forwarded_groups.split(",")

        groups_header = [group.replace(self.settings.group_prefix, "") for group in x_forwarded_groups]

        groups_available = self.available_groups()
        groups_filtered = list(set(groups_header) & set(groups_available))

        return groups_filtered

    def select(self, x_forwarded_groups: str | None) -> str:
        groups = self._parse_group_header(x_forwarded_groups=x_forwarded_groups)

        if len(groups) == 0:
            return self.settings.group_default_name

        groups_available = self.available_groups()
        for group in groups_available:
            if group in groups:
                group_selected = group
                break
        else:
            group_selected = self.settings.group_default_name

        return group_selected

    @timeout_decorator.timeout(5, timeout_exception=Exception)
    def get_config(
        self,
        prefix: str | None = None,
        name: str | None = None,
        namespace: str | None = None,
    ) -> GroupConfig:
        if not prefix:
            prefix = self.settings.group_prefix

        if not name:
            name = self.settings.group_default_name

        if not namespace:
            namespace = self.settings.group_default_namespace

        group_map_name = f"{prefix}{name}"

        try:
            client = k8s.client.CoreV1Api()
            cm = client.read_namespaced_config_map(name=group_map_name, namespace=namespace)
        except ApiException as e:
            logger.error(e)
            raise ValueError(f"ConfigMap {name} not found in namespace {namespace}")

        cc = {}
        for item in GroupConfig.__fields__:
            cc[item] = cm.data.get(item.upper(), getattr(self.settings, item, None))

        return GroupConfig(**cc)


def get_group_service(service: Annotated[GroupService, Depends(GroupService)]) -> GroupService:
    return service
