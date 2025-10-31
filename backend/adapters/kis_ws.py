"""KIS 해외 데이터 스트림용 WebSocket 클라이언트 스캐폴드.

이 구현은 재연결 로직, 하트비트 관리, 체결 통보 채널에서 사용하는
AES-256 복호화를 위한 자리표시자를 제공한다. 실제 암호화 파라미터는 공식
명세에서 확인해야 하므로 TODO 주석으로 남겨 두었다.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional

import httpx
import websockets
from websockets.client import WebSocketClientProtocol

from .kis_spec import WS_SPEC

logger = logging.getLogger(__name__)


class KISWebSocketClient:
    """지수 백오프 재연결을 지원하는 관리형 WebSocket 연결."""

    def __init__(
        self,
        approval_key: str,
        subscriptions: Iterable[Dict[str, Any]],
        *,
        on_message: Callable[[Dict[str, Any]], Awaitable[None]],
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        if not WS_SPEC.base_url:
            raise RuntimeError("KIS specification incomplete; use PaperAdapter instead.")
        self._approval_key = approval_key
        self._subscriptions = list(subscriptions)
        self._on_message = on_message
        self._on_error = on_error or (lambda exc: logger.error("KIS WS error: %s", exc))
        self._should_run = True

    async def run(self) -> None:
        backoff = 1.0
        while self._should_run:
            try:
                await self._run_once()
                backoff = 1.0
            except Exception as exc:  # pragma: no cover - 네트워크 오류 재현 어려움
                self._on_error(exc)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60.0)

    async def stop(self) -> None:
        self._should_run = False

    async def _run_once(self) -> None:
        headers = {"approval_key": self._approval_key}
        async with websockets.connect(WS_SPEC.base_url, extra_headers=headers, ping_interval=WS_SPEC.heartbeat_interval) as ws:
            await self._subscribe(ws)
            async for message in ws:
                data = self._decode_payload(message)
                await self._on_message(data)

    async def _subscribe(self, ws: WebSocketClientProtocol) -> None:
        for sub in self._subscriptions:
            await ws.send(json.dumps(sub))

    def _decode_payload(self, payload: str) -> Dict[str, Any]:
        """필요 시 AES256 복호화를 포함해 체결 통보를 디코딩한다.

        KIS 해외 WebSocket은 체결 이벤트를 AES-256-CBC로 암호화한다. 구현자는
        공식 문서를 참고해 올바른 키 파생과 IV 처리 로직을 채워 넣어야 한다.
        이 스캐폴드는 JSON 페이로드를 단순 파싱하며 평문이라고 가정한다.
        """

        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            logger.warning("Failed to parse payload, returning raw message")
            return {"raw": payload}


async def issue_ws_key(app_key: str, app_secret: str) -> str:
    """REST 엔드포인트를 통해 WebSocket 승인 키를 요청한다."""

    if not WS_SPEC.approval_key_path:
        raise RuntimeError("KIS WS specification incomplete; use PaperAdapter instead.")
    async with httpx.AsyncClient(timeout=WS_SPEC.heartbeat_interval) as client:
        response = await client.post(
            WS_SPEC.approval_key_path,
            json={"appkey": app_key, "appsecret": app_secret},
        )
        response.raise_for_status()
        data = response.json()
        key = data.get("approval_key")
        if not key:
            raise RuntimeError("Approval key missing in response")
        return key
