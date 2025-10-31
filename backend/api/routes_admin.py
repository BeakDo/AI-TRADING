"""거래 온오프와 파라미터 수정을 담당하는 관리자용 라우트."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..core.settings import (
    ensure_credentials_file_permissions,
    refresh_kis_credentials,
    settings,
)

router = APIRouter()


class ToggleRequest(BaseModel):
    enabled: bool


class ParamsRequest(BaseModel):
    entry_score_th: float


class KisCredentialsRequest(BaseModel):
    appkey: str = Field(..., description="KIS 앱키")
    appsecret: str = Field(..., description="KIS 앱시크릿")
    account_no8: str = Field(..., description="8자리 계좌 구분")
    account_prod2: str = Field(..., description="2자리 상품 코드")
    is_paper: bool = Field(default=True, description="모의/실전 여부")


def _credentials_path() -> Path:
    return Path(settings.KIS_CREDENTIALS_FILE).expanduser()


def _mask_secret(value: str, keep: int = 3) -> str:
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    hidden = max(len(value) - keep, 0)
    return f"{value[:keep]}{'*' * hidden}"


def _build_credentials_status() -> Dict[str, Any]:
    path = _credentials_path()
    has_file = path.exists()
    return {
        "has_credentials": has_file and bool(settings.KIS_APPKEY and settings.KIS_APPSECRET),
        "appkey_preview": _mask_secret(settings.KIS_APPKEY),
        "account_no8_preview": _mask_secret(settings.KIS_ACCOUNT_NO8),
        "account_prod2_preview": _mask_secret(settings.KIS_ACCOUNT_PROD2),
        "is_paper": settings.KIS_IS_PAPER,
    }


@router.post("/trade/enable")
async def trade_enable(req: ToggleRequest) -> Dict[str, Any]:
    return {"enabled": req.enabled}


@router.post("/params")
async def update_params(req: ParamsRequest) -> Dict[str, Any]:
    return {"entry_score_th": req.entry_score_th}


@router.get("/kis/credentials")
async def read_kis_credentials() -> Dict[str, Any]:
    refresh_kis_credentials(settings)
    return _build_credentials_status()


@router.post("/kis/credentials")
async def save_kis_credentials(payload: KisCredentialsRequest) -> Dict[str, Any]:
    if isinstance(payload, dict):  # FastAPI 스텁 환경 호환
        payload = KisCredentialsRequest(**payload)

    path = _credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("w", encoding="utf-8") as fp:
            json.dump(payload.model_dump(), fp, ensure_ascii=False, indent=2)
    except OSError as exc:  # pragma: no cover - 파일 시스템 예외 처리
        raise HTTPException(status_code=500, detail="KIS 자격 증명을 저장하지 못했습니다.") from exc

    ensure_credentials_file_permissions(path)
    refresh_kis_credentials(settings)
    return _build_credentials_status()
