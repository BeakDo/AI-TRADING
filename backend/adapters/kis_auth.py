"""KIS OpenAPI 인증 헬퍼 모듈.

이 모듈은 액세스 토큰과 WebSocket 승인 키를 관리하는 도우미를 제공한다.
명세 상수가 비어 있는 경우 :class:`RuntimeError`를 발생시켜 호출자가
PaperAdapter로 폴백하도록 안내한다.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

import httpx

from .kis_spec import AUTH_SPEC, WS_SPEC

logger = logging.getLogger(__name__)


class KISAuthError(RuntimeError):
    """KIS 인증이 실패했을 때 발생하는 예외."""


class KISAuthManager:
    """OAuth 토큰과 WS 승인 키를 갱신하는 상태 저장 매니저."""

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        account_no8: str,
        account_prod2: str,
        is_paper: bool,
        *,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        if not AUTH_SPEC.token_url:
            raise RuntimeError("KIS specification incomplete; use PaperAdapter instead.")
        if not WS_SPEC.approval_key_path:
            raise RuntimeError("KIS WebSocket specification incomplete; use PaperAdapter instead.")
        self._app_key = app_key
        self._app_secret = app_secret
        self._account_no8 = account_no8
        self._account_prod2 = account_prod2
        self._is_paper = is_paper
        self._token: Optional[str] = None
        self._token_expiry: float = 0
        self._approval_key: Optional[str] = None
        self._approval_expiry: float = 0
        self._client = client or httpx.AsyncClient(timeout=AUTH_SPEC.timeout_seconds if hasattr(AUTH_SPEC, "timeout_seconds") else 10.0)
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        await self._client.aclose()

    async def get_access_token(self) -> str:
        async with self._lock:
            if self._token and time.time() < self._token_expiry - 60:
                return self._token
            await self._refresh_token()
            assert self._token is not None
            return self._token

    async def get_ws_approval_key(self) -> str:
        async with self._lock:
            if self._approval_key and time.time() < self._approval_expiry - 60:
                return self._approval_key
            await self._refresh_approval_key()
            assert self._approval_key is not None
            return self._approval_key

    async def _refresh_token(self) -> None:
        payload = {
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }
        logger.info("Requesting new KIS access token")
        response = await self._client.post(AUTH_SPEC.token_url, json=payload)
        if response.status_code != 200:
            raise KISAuthError(f"Token request failed: {response.status_code} {response.text}")
        data = response.json()
        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 0))
        if not token or not expires_in:
            raise KISAuthError("Token response missing fields")
        self._token = token
        self._token_expiry = time.time() + expires_in
        logger.info("Received KIS access token valid for %s seconds", expires_in)

    async def _refresh_approval_key(self) -> None:
        payload = {
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }
        logger.info("Requesting new KIS WS approval key")
        response = await self._client.post(WS_SPEC.approval_key_path, json=payload)
        if response.status_code != 200:
            raise KISAuthError(
                f"Approval key request failed: {response.status_code} {response.text}"
            )
        data = response.json()
        key = data.get("approval_key")
        if not key:
            raise KISAuthError("Approval key response missing field")
        self._approval_key = key
        self._approval_expiry = time.time() + 24 * 60 * 60
        logger.info("Received KIS approval key valid for 24 hours")
