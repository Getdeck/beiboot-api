from functools import lru_cache

from config.types import Config
from pydantic import BaseSettings


class Settings(BaseSettings, Config):
    k8s_config_file: str = "./kubeconfig.yaml"

    # sentry
    sentry_dsn: str | None
    sentry_environment: str | None

    # config
    config_prefix: str = "api-config-"
    config_default_name: str = "default"
    config_default_namespace: str = "getdeck"

    # group
    group_prefix: str = "api-group-"
    group_default_name: str = "default"
    group_default_namespace: str = "getdeck"
    group_role_prefix: str = "api-group-"

    # user
    user_cluster_limit: int = 1

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
