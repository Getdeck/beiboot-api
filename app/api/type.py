from pydantic import BaseModel
from beiboot.types import BeibootState


class ClusterData(BaseModel):
    name: str


class BeibootResponse(BaseModel):
    name: str
    state: BeibootState
