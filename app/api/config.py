from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None


settings = Settings()
