"""환경 변수 및 저장 파일에서 설정을 불러오는 애플리케이션 구성."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # KIS 설정
    KIS_APPKEY: str = ""
    KIS_APPSECRET: str = ""
    KIS_ACCOUNT_NO8: str = ""
    KIS_ACCOUNT_PROD2: str = ""
    KIS_IS_PAPER: bool = True
    KIS_CREDENTIALS_FILE: str = "infra/kis_credentials.json"

    # 백엔드 설정
    POSTGRES_DSN: str = "postgresql+psycopg://user:pass@db:5432/trader"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me"
    DATA_PROVIDER: str = "KIS"

    # 전략 기본값
    TP_CHOICES: List[float] = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
    TS_CHOICES_MIN: List[int] = [10, 15, 20]
    SL_ATR_CHOICES: List[float] = [1.0, 1.25, 1.5, 2.0]
    ENTRY_SCORE_TH: float = 0.6
    MAX_DAILY_DRAWDOWN: float = 500.0
    MAX_CONCURRENT_POS: int = 3


_KIS_FIELD_MAP: Mapping[str, str] = {
    "appkey": "KIS_APPKEY",
    "appsecret": "KIS_APPSECRET",
    "account_no8": "KIS_ACCOUNT_NO8",
    "account_prod2": "KIS_ACCOUNT_PROD2",
    "is_paper": "KIS_IS_PAPER",
}


def _load_kis_credentials_from_file(path: Path) -> Dict[str, Any]:
    """저장된 KIS 인증 정보를 읽어 들인다."""

    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as fp:
            loaded: Dict[str, Any] = json.load(fp)
    except (OSError, json.JSONDecodeError):
        return {}

    return loaded


def _apply_kis_credentials(settings_obj: Settings, data: Mapping[str, Any]) -> None:
    """불러온 KIS 인증 정보를 설정 객체에 반영한다."""

    for source_key, attr_name in _KIS_FIELD_MAP.items():
        if source_key not in data:
            continue
        value = data[source_key]
        if value in ("", None):
            continue
        if attr_name == "KIS_IS_PAPER":
            setattr(settings_obj, attr_name, bool(value))
        else:
            setattr(settings_obj, attr_name, str(value))


def refresh_kis_credentials(settings_obj: Settings) -> None:
    """파일에서 KIS 인증 정보를 다시 읽어 설정을 갱신한다."""

    credentials_path = Path(settings_obj.KIS_CREDENTIALS_FILE).expanduser()
    data = _load_kis_credentials_from_file(credentials_path)
    _apply_kis_credentials(settings_obj, data)


@lru_cache()
def get_settings() -> Settings:
    config = Settings()
    refresh_kis_credentials(config)
    return config


settings = get_settings()


def ensure_credentials_file_permissions(path: Path) -> None:
    """민감 정보 파일 권한을 600 수준으로 제한한다."""

    try:
        os.chmod(path, 0o600)
    except OSError:
        # 일부 파일 시스템이나 운영체제에서는 권한 설정을 변경하지 못할 수 있다.
        return
