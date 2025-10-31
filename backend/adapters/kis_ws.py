"""WebSocket client scaffold for the KIS overseas data streams.

The implementation provides reconnection logic, heartbeat management and a
placeholder for AES-256 decryption used by the execution notification channel.
The actual encryption parameters must be sourced from the official
specification and are therefore left as TODO comments.
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
    """Managed WebSocket connection with exponential backoff reconnection."""

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
            except Exception as exc:  # pragma: no cover - network errors hard to simulate
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
        """Decode execution notifications with optional AES256 decryption.

        The KIS overseas WebSocket encrypts execution events using AES-256-CBC.
        Implementers must fill in the correct key derivation and IV handling
        based on the official documentation.  The scaffold simply parses JSON
        payloads and assumes they are plaintext.
        """

        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            logger.warning("Failed to parse payload, returning raw message")
            return {"raw": payload}


async def issue_ws_key(app_key: str, app_secret: str) -> str:
    """Request a WebSocket approval key using the REST endpoint."""

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
