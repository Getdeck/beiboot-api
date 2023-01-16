from pydantic import BaseModel


class ClusterData(BaseModel):
    name: str


class BeibootResponse(BaseModel):
    state: str
