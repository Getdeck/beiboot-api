from cluster_config.types import ClusterConfig
from pydantic import BaseSettings


class Settings(BaseSettings, ClusterConfig):
    k8s_config_file: str = "./kubeconfig.yaml"

    # sentry
    sentry_dsn: str | None
    sentry_environment: str | None

    # cluster config (cc)
    cc_default_name: str = "beiboot-api-config"
    cc_default_namespace: str = "getdeck"

    class Config:
        env_file = ".env"


settings = Settings()
