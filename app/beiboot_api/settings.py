from functools import lru_cache
from typing import List

from config.types import Config
from pydantic import BaseSettings, validator


class Settings(BaseSettings, Config):
    k8s_config_file: str = "./kubeconfig.yaml"

    # sentry
    sentry_dsn: str | None
    sentry_environment: str | None

    # groups
    groups: List[str] = ["admin", "user"]

    # config
    config_prefix: str = "config-"
    config_default_name: str = "default"
    config_default_namespace: str = "getdeck"

    class Config:
        env_file = ".env"

    @validator("groups", pre=True)
    def groups_validator(cls, v):
        if type(v) == str:
            v = v.split(",")
        return v


@lru_cache()
def get_settings():
    return Settings()
