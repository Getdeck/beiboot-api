from enum import Enum
from typing import Dict, List, Optional

from beiboot.types import BeibootState
from pydantic import BaseModel


class ClusterParameter(Enum):
    K8S_VERSION = "K8S_VERSION"
    NODE_COUNT = "NODE_COUNT"
    LIFETIME = "LIFETIME"
    SESSION_TIMEOUT = "SESSION_TIMEOUT"
    # "SERVER_RESOURCES_REQUESTS_CPU"
    # "SERVER_RESOURCES_REQUESTS_MEMORY"


class Parameter(BaseModel):
    name: ClusterParameter
    value: str


# class Parameters(BaseModel):
#     k8s_version: Parameter(name=ClusterParameter.K8S_VERSION)


class ClusterRequest(BaseModel):
    name: str
    parameters: Optional[List[Parameter]] = None
    ports: Optional[List[str]] = None
    labels: Dict[str, str] = {}


class ClusterResponse(BaseModel):
    name: str
    state: BeibootState
