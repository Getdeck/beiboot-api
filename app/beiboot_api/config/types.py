import logging
from datetime import timedelta
from decimal import Decimal
from typing import List

from cluster.helpers import convert_to_timedelta
from kubernetes.utils.quantity import parse_quantity
from pydantic import BaseModel, Field, validator
from semver import Version

logger = logging.getLogger("uvicorn.beiboot")


class Config(BaseModel):
    k8s_versions: List[str] | None = Field(default=None, env="cd_k8s_versions")
    node_count_min: int | None = Field(default=1, env="cd_node_count_min")
    node_count_max: int | None = Field(default=3, env="cd_node_count_max")
    lifetime_limit: timedelta | None = Field(default=timedelta(hours=4), env="cd_lifetime_limit")
    session_timeout_limit: timedelta | None = Field(default=timedelta(minutes=30), env="cd_session_timeout_limit")
    cluster_request_timeout_limit: timedelta | None = Field(
        default=timedelta(minutes=5), env="cd_cluster_request_timeout_limit"
    )

    # server resources + storage
    server_resources_requests_cpu_min: Decimal | None = Field(
        default=None,
        env="cd_server_resources_requests_cpu_min",
    )
    server_resources_requests_cpu_max: Decimal | None = Field(
        default=None,
        env="cd_server_resources_requests_cpu_max",
    )
    server_resources_requests_memory_min: Decimal | None = Field(
        default=None,
        env="cd_server_resources_requests_memory_min",
    )
    server_resources_requests_memory_max: Decimal | None = Field(
        default=None,
        env="cd_server_resources_requests_memory_max",
    )
    server_resources_limits_cpu_min: Decimal | None = Field(
        default=None,
        env="cd_server_resources_limits_cpu_min",
    )
    server_resources_limits_cpu_max: Decimal | None = Field(
        default=None,
        env="cd_server_resources_limits_cpu_max",
    )
    server_resources_limits_memory_min: Decimal | None = Field(
        default=None,
        env="cd_server_resources_limits_memory_min",
    )
    server_resources_limits_memory_max: Decimal | None = Field(
        default=None,
        env="cd_server_resources_limits_memory_max",
    )
    server_storage_requests_min: Decimal | None = Field(
        default=None,
        env="cd_server_storage_requests_min",
    )
    server_storage_requests_max: Decimal | None = Field(
        default=None,
        env="cd_server_storage_requests_max",
    )

    # node resources + storage
    node_resources_requests_cpu_min: Decimal | None = Field(
        default=None,
        env="cd_node_resources_requests_cpu_min",
    )
    node_resources_requests_cpu_max: Decimal | None = Field(
        default=None,
        env="cd_node_resources_requests_cpu_max",
    )
    node_resources_requests_memory_min: Decimal | None = Field(
        default=None,
        env="cd_node_resources_requests_memory_min",
    )
    node_resources_requests_memory_max: Decimal | None = Field(
        default=None,
        env="cd_node_resources_requests_memory_max",
    )
    node_resources_limits_cpu_min: Decimal | None = Field(
        default=None,
        env="cd_node_resources_limits_cpu_min",
    )
    node_resources_limits_cpu_max: Decimal | None = Field(
        default=None,
        env="cd_node_resources_limits_cpu_max",
    )
    node_resources_limits_memory_min: Decimal | None = Field(
        default=None,
        env="cd_node_resources_limits_memory_min",
    )
    node_resources_limits_memory_max: Decimal | None = Field(
        default=None,
        env="cd_node_resources_limits_memory_max",
    )
    node_storage_requests_min: Decimal | None = Field(
        default=None,
        env="cd_node_storage_requests_min",
    )
    node_storage_requests_max: Decimal | None = Field(
        default=None,
        env="cd_node_storage_requests_max",
    )

    @validator("k8s_versions", pre=True)
    def k8s_versions_validator(cls, v):
        if not v:
            return None

        if type(v) == str:
            v = v.split(",")

        for version in v:
            try:
                _ = Version.parse(version)
            except TypeError:
                raise ValueError(f"Invalid version: '{version}'.")

        return v

    @validator("node_count_min")
    def node_count_validator(cls, v):
        if v < 1:
            return 1
        return v

    @validator("lifetime_limit", "session_timeout_limit", "cluster_request_timeout_limit", pre=True)
    def timedelta_validator(cls, v, values, field):
        if type(v) == timedelta:
            return v

        try:
            td = convert_to_timedelta(v)
        except ValueError:
            raise ValueError(f"Invalid {field.name}: '{v}'.")

        return td

    @validator(
        "server_resources_requests_cpu_min",
        "server_resources_requests_cpu_max",
        "server_resources_limits_cpu_min",
        "server_resources_limits_cpu_max",
        "node_resources_requests_cpu_min",
        "node_resources_requests_cpu_max",
        "node_resources_limits_cpu_min",
        "node_resources_limits_cpu_max",
        pre=True,
    )
    def compute_validator(cls, v, values, field):
        if not v:
            return None

        if v.endswith(("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "k", "K", "M", "G", "T", "P", "E")):
            raise ValueError(f"Invalid {field.name}: '{v}'.")

        try:
            v = parse_quantity(v)
        except ValueError:
            logger.warning(f"Invalid {field.name}: '{v}'.")
            return None

        return v

    @validator(
        "server_resources_requests_memory_min",
        "server_resources_requests_memory_max",
        "server_resources_limits_memory_min",
        "server_resources_limits_memory_max",
        "server_storage_requests_min",
        "server_storage_requests_max",
        "node_resources_requests_memory_min",
        "node_resources_requests_memory_max",
        "node_resources_limits_memory_min",
        "node_resources_limits_memory_max",
        "node_storage_requests_min",
        "node_storage_requests_max",
        pre=True,
    )
    def memory_validator(cls, v, values, field):
        if not v:
            return None

        if not v.endswith(("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "k", "K", "M", "G", "T", "P", "E")):
            raise ValueError(f"Invalid {field.name}: '{v}'.")

        try:
            v = parse_quantity(v)
        except ValueError:
            logger.warning(f"Invalid {field.name}: '{v}'.")
            return None

        return v


class ConfigInfoResponse(BaseModel):
    default: bool = True
    name: str = "default"
    config: Config | None
