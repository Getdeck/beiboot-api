from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None

    # rest config
    rc_default_name: str = "beiboot-rest-config"
    rc_default_namespace: str = "getdeck"
    rc_cluster_lifetime_limit: Optional[str] = None
    rc_cluster_node_limit: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
