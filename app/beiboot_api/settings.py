from functools import lru_cache

from config.types import Config
from pydantic import BaseSettings


class Settings(BaseSettings, Config):
    k8s_config_file: str = "./kubeconfig.yaml"

    # sentry
    sentry_dsn: str | None
    sentry_environment: str | None

    # groups
    group_default: str = "default"

    # config
    config_prefix: str = "config-"
    config_default_name: str = "default"
    config_default_namespace: str = "getdeck"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
