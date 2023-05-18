import logging
from typing import Annotated, List
from uuid import uuid4

from beiboot import api
from beiboot.types import Beiboot, BeibootParameters, BeibootProvider, BeibootRequest
from cluster.types import ClusterRequest, Labels, Parameters
from config.types import Config
from fastapi import Depends, Request
from settings import Settings, get_settings

logger = logging.getLogger("uvicorn.beiboot")


class ClusterService:
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.settings = settings

    def create_new_cluster_id(self) -> str:
        cluster_id = uuid4()

        beiboot = self.get(cluster_id=cluster_id)
        if beiboot:
            raise Exception(detail="Cluster ID collision. Please try again.")

        return cluster_id

    def list(self, labels: Labels = None) -> List[Beiboot]:
        if not labels:
            labels = Labels()

        beiboots = api.read_all(labels.dict(exclude_none=True))
        return beiboots

    def get(self, cluster_id: str, labels: Labels = None) -> Beiboot | None:
        beiboots = self.list(labels=labels)
        for bbt in beiboots:
            if bbt.name == cluster_id:
                return bbt
        else:
            return None

    def create(self, request: Request, cluster_request: ClusterRequest) -> Beiboot:
        # validate labels + parameters
        labels = Labels(name=cluster_request.name, user=request.state.user)

        cluster_config = Config(**self.settings.dict())
        tmp = {str(parameter.name.value): parameter for parameter in cluster_request.parameters}

        try:
            parameters = Parameters(cluster_config=cluster_config, **tmp)
        except Exception as e:
            raise ValueError(detail=e.errors())

        # generate new cluster_id
        cluster_id = self.create_new_cluster_id()

        # cluster creation
        req = BeibootRequest(
            name=str(cluster_id),
            provider=BeibootProvider.K3S,
            parameters=BeibootParameters(
                k8sVersion=parameters.k8s_version.value,
                nodes=parameters.node_count.value,
                maxLifetime=parameters.lifetime.value,
                maxSessionTimeout=parameters.session_timeout.value,
            ),
            labels=labels.dict(exclude_none=True),
        )
        beiboot = api.create(req)
        return beiboot

    def delete(self, cluster_id: str, labels: Labels = None):
        beiboot = self.get(cluster_id=cluster_id, labels=labels)
        if not beiboot:
            raise ValueError("Cluster not found")

        api.delete_by_name(name=cluster_id)


def get_cluster_service(service: Annotated[ClusterService, Depends(ClusterService)]) -> ClusterService:
    return service
