from pydantic import BaseModel, Field


class ClusterConfig(BaseModel):
    node_count_minimum: int | None = Field(default=1, env="cc_node_count_minimum")
    node_count_maximum: int | None = Field(env="cc_node_count_maximum")
