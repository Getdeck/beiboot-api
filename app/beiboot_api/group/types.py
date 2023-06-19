import logging

from pydantic import BaseModel, Field, validator

logger = logging.getLogger("uvicorn.beiboot")


class GroupConfig(BaseModel):
    group_cluster_limit: int | None = Field(default=5)
    user_cluster_limit: int | None = Field(default=0)

    @validator("group_cluster_limit", "user_cluster_limit")
    def positive_integer_validator(cls, v):
        if not v:
            return None

        if v < 0:
            return 0

        return v
