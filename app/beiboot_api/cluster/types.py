import logging
import re
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Union

from beiboot.types import BeibootState
from cluster.helpers import convert_to_timedelta
from config.types import Config
from kubernetes.utils.quantity import parse_quantity
from pydantic import BaseModel, Field, PrivateAttr, validator
from semver import Version
from settings import get_settings

logger = logging.getLogger("uvicorn.beiboot")


class ClusterParameter(Enum):
    K8S_VERSION = "K8S_VERSION"
    PORTS = "PORTS"
    NODE_COUNT = "NODE_COUNT"
    LIFETIME = "LIFETIME"
    SESSION_TIMEOUT = "SESSION_TIMEOUT"
    CLUSTER_READY_TIMEOUT = "CLUSTER_READY_TIMEOUT"
    SERVER_RESOURCES_REQUESTS_CPU = "SERVER_RESOURCES_REQUESTS_CPU"
    SERVER_RESOURCES_REQUESTS_MEMORY = "SERVER_RESOURCES_REQUESTS_MEMORY"
    SERVER_RESOURCES_LIMITS_CPU = "SERVER_RESOURCES_LIMITS_CPU"
    SERVER_RESOURCES_LIMITS_MEMORY = "SERVER_RESOURCES_LIMITS_MEMORY"
    SERVER_STORAGE_REQUESTS = "SERVER_STORAGE_REQUESTS"
    NODE_RESOURCES_REQUESTS_CPU = "NODE_RESOURCES_REQUESTS_CPU"
    NODE_RESOURCES_REQUESTS_MEMORY = "NODE_RESOURCES_REQUESTS_MEMORY"
    NODE_RESOURCES_LIMITS_CPU = "NODE_RESOURCES_LIMITS_CPU"
    NODE_RESOURCES_LIMITS_MEMORY = "NODE_RESOURCES_LIMITS_MEMORY"
    NODE_STORAGE_REQUESTS = "NODE_STORAGE_REQUESTS"
    GEFYRA_ENABLED = "GEFYRA_ENABLED"
    GEFYRA_ENDPOINT = "GEFYRA_ENDPOINT"
    TUNNEL_ENABLED = "TUNNEL_ENABLED"
    TUNNEL_ENDPOINT = "TUNNEL_ENDPOINT"


class Parameter(BaseModel):
    name: ClusterParameter
    value: Union[str, int, List[str], List[int]] | None


class ComputeParameter(Parameter):
    # _value_verbose: str | None = PrivateAttr(None)

    # def __init__(self, **data):
    #     super().__init__(**data)
    #     self._value_verbose = data.get("value", None)

    @validator("value", pre=True)
    def value_validator(cls, v, values, field):
        if not v:
            return v

        if v.endswith(("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "k", "K", "M", "G", "T", "P", "E")):
            raise ValueError(f"Invalid {field.name}: '{v}'.")

        try:
            v = parse_quantity(v)
        except ValueError:
            raise ValueError(f"Invalid {field.name}: '{v}'.")

        return v


class MemoryParameter(Parameter):
    @validator("value", pre=True)
    def value_validator(cls, v, values, field):
        if not v:
            return v

        if not v.endswith(("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "k", "K", "M", "G", "T", "P", "E")):
            raise ValueError(f"Invalid {field.name}: '{v}'.")

        try:
            v = parse_quantity(v)
        except ValueError:
            raise ValueError(f"Invalid {field.name}: '{v}'.")

        return v


class K8sVersion(Parameter):
    name: ClusterParameter = ClusterParameter.K8S_VERSION
    value: str | None

    @validator("value")
    def value_validator(cls, v):
        if not v:
            return v

        try:
            _ = Version.parse(v)
        except (TypeError, ValueError) as e:
            raise type(e)(f"Invalid {ClusterParameter.K8S_VERSION.value}.")

        return v


class Ports(Parameter):
    name: ClusterParameter = ClusterParameter.PORTS
    value: List[str] | None

    @validator("value")
    def value_validator(cls, v):
        if not v:
            return v

        for mapping in v:
            try:
                local, cluster = mapping.split(":")
                local = int(local)
                cluster = int(cluster)
            except ValueError:
                raise ValueError(f"Invalid {ClusterParameter.PORTS.value}: '{mapping}'.")

            if local > 65535 or local <= 0 or cluster > 65535 or cluster <= 0:
                ValueError(f"Invalid {ClusterParameter.PORTS.value}: '{mapping}'. Port out of range (0-65535).")

        # remove duplicates + 6443:6443
        v = list(set(v))
        if "6443:6443" in v:
            v.remove("6443:6443")

        return v


class NodeCount(Parameter):
    name: ClusterParameter = ClusterParameter.NODE_COUNT
    value: int | None


class Lifetime(Parameter):
    name: ClusterParameter = ClusterParameter.LIFETIME
    value: str | None

    @validator("value", pre=True)
    def value_validator(cls, v):
        try:
            _ = convert_to_timedelta(v)
        except ValueError:
            raise ValueError(f"Invalid {ClusterParameter.LIFETIME.value}: '{v}'.")

        return v


class SessionTimeout(Parameter):
    name: ClusterParameter = ClusterParameter.SESSION_TIMEOUT
    value: str | None

    @validator("value", pre=True)
    def value_validator(cls, v):
        try:
            _ = convert_to_timedelta(v)
        except ValueError:
            raise ValueError(f"Invalid {ClusterParameter.SESSION_TIMEOUT.value}: '{v}'.")

        return v


class ClusterReadyTimeout(Parameter):
    name: ClusterParameter = ClusterParameter.CLUSTER_READY_TIMEOUT
    value: int | None

    @validator("value")
    def value_validator(cls, v):
        if not v:
            return v

        if v < 0:
            raise ValueError(f"Invalid {ClusterParameter.CLUSTER_READY_TIMEOUT.value}: '{v} < 0'.")

        return v


class ServerResourcesRequestsCpu(ComputeParameter):
    name: ClusterParameter = ClusterParameter.SERVER_RESOURCES_REQUESTS_CPU
    value: Decimal | None


class ServerResourcesRequestsMemory(MemoryParameter):
    name: ClusterParameter = ClusterParameter.SERVER_RESOURCES_REQUESTS_MEMORY
    value: Decimal | None


class ServerResourcesLimitsCpu(ComputeParameter):
    name: ClusterParameter = ClusterParameter.SERVER_RESOURCES_LIMITS_CPU
    value: Decimal | None


class ServerResourcesLimitsMemory(MemoryParameter):
    name: ClusterParameter = ClusterParameter.SERVER_RESOURCES_LIMITS_MEMORY
    value: Decimal | None


class ServerStorageRequests(MemoryParameter):
    name: ClusterParameter = ClusterParameter.SERVER_STORAGE_REQUESTS
    value: Decimal | None


class NodeResourcesRequestsCpu(ComputeParameter):
    name: ClusterParameter = ClusterParameter.NODE_RESOURCES_REQUESTS_CPU
    value: Decimal | None


class NodeResourcesRequestsMemory(MemoryParameter):
    name: ClusterParameter = ClusterParameter.NODE_RESOURCES_REQUESTS_MEMORY
    value: Decimal | None


class NodeResourcesLimitsCpu(ComputeParameter):
    name: ClusterParameter = ClusterParameter.NODE_RESOURCES_LIMITS_CPU
    value: Decimal | None


class NodeResourcesLimitsMemory(MemoryParameter):
    name: ClusterParameter = ClusterParameter.NODE_RESOURCES_LIMITS_MEMORY
    value: Decimal | None


class NodeStorageRequests(MemoryParameter):
    name: ClusterParameter = ClusterParameter.NODE_STORAGE_REQUESTS
    value: Decimal | None


class GefyraEnabled(Parameter):
    name: ClusterParameter = ClusterParameter.GEFYRA_ENABLED
    value: bool | None


class GefyraEndpoint(Parameter):
    name: ClusterParameter = ClusterParameter.GEFYRA_ENDPOINT
    value: str | None


class TunnelEnabled(Parameter):
    name: ClusterParameter = ClusterParameter.TUNNEL_ENABLED
    value: bool | None


class TunnelEndpoint(Parameter):
    name: ClusterParameter = ClusterParameter.TUNNEL_ENDPOINT
    value: str | None


class Parameters(BaseModel):
    cluster_config: Config = None

    k8s_version: K8sVersion | None = Field(
        default=K8sVersion(value=None),
        alias=ClusterParameter.K8S_VERSION.value,
    )
    ports: Ports | None = Field(
        default=Ports(value=["80:80", "443:443"]),
        alias=ClusterParameter.PORTS.value,
    )
    node_count: NodeCount | None = Field(
        alias=ClusterParameter.NODE_COUNT.value,
    )
    lifetime: Lifetime | None = Field(
        default=Lifetime(value="1h"),
        alias=ClusterParameter.LIFETIME.value,
    )
    session_timeout: SessionTimeout | None = Field(
        default=SessionTimeout(value="5m"),
        alias=ClusterParameter.SESSION_TIMEOUT.value,
    )
    cluster_ready_timeout: ClusterReadyTimeout | None = Field(
        default=ClusterReadyTimeout(value=180),
        alias=ClusterParameter.CLUSTER_READY_TIMEOUT.value,
    )

    # server resources + storage
    server_resources_requests_cpu: ServerResourcesRequestsCpu | None = Field(
        default=ServerResourcesRequestsCpu(value=None),
        alias=ClusterParameter.SERVER_RESOURCES_REQUESTS_CPU.value,
    )
    server_resources_requests_memory: ServerResourcesRequestsMemory | None = Field(
        default=ServerResourcesRequestsMemory(value=None),
        alias=ClusterParameter.SERVER_RESOURCES_REQUESTS_MEMORY.value,
    )
    server_resources_limits_cpu: ServerResourcesLimitsCpu | None = Field(
        default=ServerResourcesLimitsCpu(value=None),
        alias=ClusterParameter.SERVER_RESOURCES_LIMITS_CPU.value,
    )
    server_resources_limits_memory: ServerResourcesLimitsMemory | None = Field(
        default=ServerResourcesLimitsMemory(value=None),
        alias=ClusterParameter.SERVER_RESOURCES_LIMITS_MEMORY.value,
    )
    server_storage_requests: ServerStorageRequests | None = Field(
        default=ServerStorageRequests(value=None),
        alias=ClusterParameter.SERVER_STORAGE_REQUESTS.value,
    )

    # node resources + storage
    node_resources_requests_cpu: NodeResourcesRequestsCpu | None = Field(
        default=NodeResourcesRequestsCpu(value=None),
        alias=ClusterParameter.NODE_RESOURCES_REQUESTS_CPU.value,
    )
    node_resources_requests_memory: NodeResourcesRequestsMemory | None = Field(
        default=NodeResourcesRequestsMemory(value=None),
        alias=ClusterParameter.NODE_RESOURCES_REQUESTS_MEMORY.value,
    )
    node_resources_limits_cpu: NodeResourcesLimitsCpu | None = Field(
        default=NodeResourcesLimitsCpu(value=None),
        alias=ClusterParameter.NODE_RESOURCES_LIMITS_CPU.value,
    )
    node_resources_limits_memory: NodeResourcesLimitsMemory | None = Field(
        default=NodeResourcesLimitsMemory(value=None),
        alias=ClusterParameter.NODE_RESOURCES_LIMITS_MEMORY.value,
    )
    node_storage_requests: NodeStorageRequests | None = Field(
        default=NodeStorageRequests(value=None),
        alias=ClusterParameter.NODE_STORAGE_REQUESTS.value,
    )

    # gefyra
    gefyra_enabled: GefyraEnabled | None = Field(
        default=GefyraEnabled(value=True),
        alias=ClusterParameter.GEFYRA_ENABLED.value,
    )
    gefyra_endpoint: GefyraEndpoint | None = Field(
        default=GefyraEndpoint(value=None),
        alias=ClusterParameter.GEFYRA_ENDPOINT.value,
    )

    # tunnel
    tunnel_enabled: TunnelEnabled | None = Field(
        default=TunnelEnabled(value=True),
        alias=ClusterParameter.TUNNEL_ENABLED.value,
    )
    tunnel_endpoint: TunnelEndpoint | None = Field(
        default=TunnelEndpoint(value=None),
        alias=ClusterParameter.TUNNEL_ENDPOINT.value,
    )

    @validator("cluster_config", pre=True, always=True)
    def cluster_config_validator(cls, v):
        if isinstance(v, Config):
            return v

        # default cluster config
        settings = get_settings()
        cluster_config = Config(**settings.dict())
        return cluster_config

    @validator("k8s_version")
    def k8s_version_validator(cls, v, *, values, **kwargs):
        cluster_config = values["cluster_config"]

        if not cluster_config.k8s_versions:
            return v

        if v.value not in cluster_config.k8s_versions:
            raise ValueError(f"Invalid {ClusterParameter.K8S_VERSION.value}: '{cluster_config.k8s_versions}'.")

        return v

    @validator("node_count", always=True)
    def node_count_validator(cls, v, *, values, **kwargs):
        cluster_config = values["cluster_config"]

        if not v:
            return NodeCount(value=cluster_config.node_count_min)

        if not cluster_config.node_count_min <= v.value <= (cluster_config.node_count_max or v.value):
            raise ValueError(f"Invalid {ClusterParameter.NODE_COUNT.value}.")

        return v

    @validator("lifetime", always=True)
    def lifetime_validator(cls, v, *, values, **kwargs):
        cluster_config = values["cluster_config"]

        if not cluster_config.lifetime_limit >= convert_to_timedelta(v.value):
            raise ValueError(
                f"Invalid {ClusterParameter.LIFETIME.value}: '{v.value}'. Limit: {cluster_config.lifetime_limit}"
            )

        return v

    @validator("session_timeout", always=True)
    def session_timeout_validator(cls, v, *, values, **kwargs):
        cluster_config = values["cluster_config"]

        if not cluster_config.session_timeout_limit >= convert_to_timedelta(v.value):
            raise ValueError(
                f"Invalid {ClusterParameter.SESSION_TIMEOUT.value}: '{v.value}'. Limit: {cluster_config.session_timeout_limit}"
            )

        return v

    # @validator("cluster_ready_timeout", always=True)
    # def cluster_ready_timeout_validator(cls, v, *, values, **kwargs):
    #     cluster_config = values["cluster_config"]

    #     if not cluster_config.cluster_ready_timeout_limit.total_seconds() >= v.value:
    #         raise ValueError(
    #             f"Invalid {ClusterParameter.CLUSTER_READY_TIMEOUT.value}: '{v.value}'. Limit: {cluster_config.cluster_ready_timeout_limit.total_seconds()}"
    #         )

    #     return v

    @validator(
        "server_resources_requests_cpu",
        "server_resources_requests_memory",
        "server_resources_limits_cpu",
        "server_resources_limits_memory",
        "server_storage_requests",
        always=True,
    )
    def min_max_decimal_validator(cls, v, *, values, field):
        cluster_config = values["cluster_config"]

        try:
            minimum = getattr(cluster_config, field.name + "_min")
            maximum = getattr(cluster_config, field.name + "_max")
            _class = type(Parameters.__fields__[field.name].default)
        except Exception as e:
            raise Exception(f"Validation error: {str(e)}")

        if not v.value:
            return _class(value=minimum)

        if not (minimum or v.value) <= v.value <= (maximum or v.value):
            try:
                field_name = Parameters.__fields__[field.name].default.name.value
            except Exception:
                field_name = "???"

            raise ValueError(
                f"Invalid {field_name}. Min: {minimum or '-'}. Max: {maximum or '-'}. Value: {v.value  or '-'}"
            )

        return v


class Labels(BaseModel):
    name: str | None
    user: str | None

    @validator("name", "user", always=True)
    def label_validator(cls, v, *, values, **kwargs):
        if not v:
            return v

        pattern = re.compile(r"(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?")
        if not re.fullmatch(pattern, v):
            raise ValueError(f"Invalid value: '{v}' (regex used for validation is '{pattern.pattern}').")

        return v


class ClusterRequest(BaseModel):
    name: str
    parameters: List[Parameter] | None
    labels: Labels | None


class ClusterStateResponse(BaseModel):
    id: str
    name: str | None
    state: BeibootState | None


class ClusterInfoResponse(BaseModel):
    id: str
    name: str | None
    namespace: str
    state: BeibootState | None
    sunset: datetime | None
    parameters: List[Parameter] | None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
