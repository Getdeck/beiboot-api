from pydantic import BaseModel


class ClusterCreateData(BaseModel):
    name: str = "beiboot"
