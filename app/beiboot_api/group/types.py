import logging

from pydantic import BaseModel, Field, validator

logger = logging.getLogger("uvicorn.beiboot")


class GroupConfig(BaseModel):
    user_cluster_limit: int | None = Field(default=0)

    @validator("user_cluster_limit")
    def user_cluster_limit_validator(cls, v):
        if v < 0:
            return 0
        return v
