from typing import List

from pydantic import BaseModel, Field, validator
from semver import Version


class Config(BaseModel):
    k8s_versions: List[str] | None = Field(default=None, env="cd_k8s_versions")
    node_count_min: int | None = Field(default=1, env="cd_node_count_min")
    node_count_max: int | None = Field(default=3, env="cd_node_count_max")

    @validator("k8s_versions", pre=True)
    def k8s_versions_validator(cls, v):
        if not v:
            return None

        if type(v) == str:
            v = v.split(",")

        for version in v:
            try:
                _ = Version.parse(version)
            except TypeError:
                raise ValueError(f"Invalid version: '{version}'.")

        return v

    @validator("node_count_min")
    def node_count_validator(cls, v):
        if v < 1:
            return 1
        return v


class ConfigInfoResponse(BaseModel):
    default: bool = True
    name: str = "default"
    config: Config | None
