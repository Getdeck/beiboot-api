from enum import Enum
from typing import Dict, List, Union

import semver
from beiboot.types import BeibootState
from cluster_config.types import ClusterConfig
from config import settings
from pydantic import BaseModel, Field, validator


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
    cluster_config: ClusterConfig = None

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
        if isinstance(v, ClusterConfig):
            return v

        # default cluster config
        cluster_config = ClusterConfig(**settings.dict())
        return cluster_config

    @validator("k8s_version")
    def k8s_version_validator(cls, v, *, values, **kwargs):
        cluster_config = values["cluster_config"]

        try:
            ver = semver.Version.parse(v.value)
        except (TypeError, ValueError) as e:
            raise type(e)(f"Invalid {ClusterParameter.K8S_VERSION.value}.")

        if cluster_config.k8s_version_min > ver:
            raise ValueError(f"Invalid {ClusterParameter.K8S_VERSION.value} - min: '{cluster_config.k8s_version_min}'.")

        if cluster_config.k8s_version_max:
            if cluster_config.k8s_version_max <= ver:
                raise ValueError(
                    f"Invalid {ClusterParameter.K8S_VERSION.value} - max: '{cluster_config.k8s_version_max}'."
                )

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
    user: str | None = None


class ClusterRequest(BaseModel):
    name: str
    parameters: List[Union[StringParameter, IntegerParameter]] | None
    ports: List[str] | None
    labels: Labels | None


class ClusterStateResponse(BaseModel):
    name: str
    state: BeibootState | None


class ClusterInfoResponse(BaseModel):
    name: str
    namespace: str
    state: BeibootState | None
    parameters: List[Union[StringParameter, IntegerParameter]] | None
