from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    k8s_config_file: str = "./kubeconfig.yaml"

    # sentry
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None

    # cluster config (cc)
    cc_default_name: str = "beiboot-api-config"
    cc_default_namespace: str = "getdeck"
    cc_cluster_lifetime_limit: Optional[str] = None
    cc_cluster_node_limit: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
