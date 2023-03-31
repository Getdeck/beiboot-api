from pydantic import BaseModel, Field, validator
from semver import VersionInfo


class ClusterConfig(BaseModel):
    k8s_version_min: str | None = Field(default="1.24.0", env="cc_k8s_version_min")
    k8s_version_max: str | None = Field(env="cc_k8s_version_max")
    node_count_min: int | None = Field(default=1, env="cc_node_count_min")
    node_count_max: int | None = Field(default=3, env="cc_node_count_max")

    @validator("k8s_version_min", "k8s_version_max")
    def k8s_version_validator(cls, v):
        if not v:
            return None

        try:
            _ = VersionInfo.parse(v)
        except TypeError:
            raise ValueError("Invalid version.")

        return v

    @validator("node_count_min")
    def node_count_validator(cls, v):
        if v < 1:
            return 1
        return v
