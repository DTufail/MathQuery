from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # GROBID
    grobid_url: str = "http://localhost:8070"

    # Mathpix
    mathpix_app_id: Optional[str] = None
    mathpix_app_key: Optional[str] = None

    # General
    request_timeout_seconds: int = 60

    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_prefix="MQ_", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]