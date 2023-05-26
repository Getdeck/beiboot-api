import re
from datetime import timedelta
from enum import Enum
from typing import List, Union

from beiboot.types import BeibootState
from cluster.helpers import convert_to_timedelta
from config.types import Config
from pydantic import BaseModel, Field, validator
from semver import Version
from settings import get_settings


class ClusterParameter(Enum):
    K8S_VERSION = "K8S_VERSION"
    PORTS = "PORTS"
    NODE_COUNT = "NODE_COUNT"
    LIFETIME = "LIFETIME"
    SESSION_TIMEOUT = "SESSION_TIMEOUT"
    # "SERVER_RESOURCES_REQUESTS_CPU"
    # "SERVER_RESOURCES_REQUESTS_MEMORY"


class Parameter(BaseModel):
    name: ClusterParameter
    value: Union[str, int, List[str], List[int]] | None


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
    parameters: List[Parameter] | None
