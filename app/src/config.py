from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    config_file_location: str = "/app/kubeconfig.yaml"
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
