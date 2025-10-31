"""Application configuration loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # KIS
    KIS_APPKEY: str = ""
    KIS_APPSECRET: str = ""
    KIS_ACCOUNT_NO8: str = ""
    KIS_ACCOUNT_PROD2: str = ""
    KIS_IS_PAPER: bool = True

    # Backend
    POSTGRES_DSN: str = "postgresql+psycopg://user:pass@db:5432/trader"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me"
    DATA_PROVIDER: str = "KIS"

    # Strategy defaults
    TP_CHOICES: List[float] = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
    TS_CHOICES_MIN: List[int] = [10, 15, 20]
    SL_ATR_CHOICES: List[float] = [1.0, 1.25, 1.5, 2.0]
    ENTRY_SCORE_TH: float = 0.6
    MAX_DAILY_DRAWDOWN: float = 500.0
    MAX_CONCURRENT_POS: int = 3


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
