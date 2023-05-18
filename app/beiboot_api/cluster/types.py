import re
from enum import Enum
from typing import List, Union

from beiboot.types import BeibootState
from config.types import Config
from pydantic import BaseModel, Field, validator
from semver import Version
from settings import get_settings


class ClusterParameter(Enum):
    K8S_VERSION = "K8S_VERSION"
    NODE_COUNT = "NODE_COUNT"
    LIFETIME = "LIFETIME"
    SESSION_TIMEOUT = "SESSION_TIMEOUT"
    # "SERVER_RESOURCES_REQUESTS_CPU"
    # "SERVER_RESOURCES_REQUESTS_MEMORY"


class StringParameter(BaseModel):
    name: ClusterParameter
    value: str | None


class IntegerParameter(BaseModel):
    name: ClusterParameter
    value: int | None


class Parameters(BaseModel):
    cluster_config: Config = None

    k8s_version: StringParameter | None = Field(
        default=StringParameter(name=ClusterParameter.K8S_VERSION.value, value=None),
        alias=ClusterParameter.K8S_VERSION.value,
    )
    node_count: IntegerParameter | None = Field(
        alias=ClusterParameter.NODE_COUNT.value,
    )
    lifetime: StringParameter | None = Field(
        default=StringParameter(name=ClusterParameter.LIFETIME.value, value=None),
        alias=ClusterParameter.LIFETIME.value,
    )
    session_timeout: StringParameter | None = Field(
        default=StringParameter(name=ClusterParameter.SESSION_TIMEOUT.value, value=None),
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

        try:
            _ = Version.parse(v.value)
        except (TypeError, ValueError) as e:
            raise type(e)(f"Invalid {ClusterParameter.K8S_VERSION.value}.")

        if not cluster_config.k8s_versions:
            return v

        if v.value not in cluster_config.k8s_versions:
            raise ValueError(f"Invalid {ClusterParameter.K8S_VERSION.value}: '{cluster_config.k8s_versions}'.")

        return v

    @validator("node_count", always=True)
    def node_count_validator(cls, v, *, values, **kwargs):
        cluster_config = values["cluster_config"]

        if not v:
            return IntegerParameter(name=ClusterParameter.NODE_COUNT.value, value=cluster_config.node_count_min)

        if not cluster_config.node_count_min <= v.value <= (cluster_config.node_count_max or v.value):
            raise ValueError(f"Invalid {ClusterParameter.NODE_COUNT.value}.")

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


class ClusterRequest(BaseModel):
    name: str
    parameters: List[Union[StringParameter, IntegerParameter]] | None
    ports: List[str] | None
    labels: Labels | None


class ClusterStateResponse(BaseModel):
    id: str
    name: str | None
    state: BeibootState | None


class ClusterInfoResponse(BaseModel):
    name: str
    namespace: str
    state: BeibootState | None
    parameters: List[Union[StringParameter, IntegerParameter]] | None
