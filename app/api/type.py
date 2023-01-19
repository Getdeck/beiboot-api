from typing import Dict, Optional
from pydantic import BaseModel
from beiboot import types as bbt_dataclass


class BeibootParameters(BaseModel):
    k8sVersion: Optional[str]
    ports: Optional[list[str]]
    nodes: Optional[int] = 1
    maxLifetime: Optional[str]
    maxSessionTimeout: Optional[str]
    # clusterReadyTimeout: Optional[int] = field(default_factory=lambda: default_configuration.CLUSTER_CREATION_TIMEOUT)
    serverResources: Optional[dict[str, dict[str, str]]] = {"requests": {"cpu": "0.25", "memory": "0.25Gi"}}
    nodeResources: Optional[dict[str, dict[str, str]]] = {"requests": {"cpu": "0.25", "memory": "0.25Gi"}}
    serverStorageRequests: Optional[str] = "500Mi"
    nodeStorageRequests: Optional[str]
    # gefyra: GefyraParams = field(default_factory=lambda: GefyraParams())
    # tunnel: Optional[TunnelParams] = field(default_factory=lambda: TunnelParams())


class BeibootRequest(BaseModel):
    name: str
    provider: bbt_dataclass.BeibootProvider = bbt_dataclass.BeibootProvider.K3S
    parameters: BeibootParameters = BeibootParameters()
    labels: Dict[str, str] = {}


class BeibootResponse(BaseModel):
    name: str
    state: bbt_dataclass.BeibootState
    mtls_files: dict = {}
