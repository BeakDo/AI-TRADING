"""Minimal httpx stub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Response:
    status_code: int
    _json: Dict[str, Any]
    text: str = ""

    def json(self) -> Dict[str, Any]:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}: {self.text}")


class AsyncClient:
    def __init__(self, *, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = base_url
        self.timeout = timeout

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def post(self, url: str, json: Optional[Dict[str, Any]] = None) -> Response:
        return Response(status_code=200, _json={})

    async def get(self, url: str) -> Response:
        return Response(status_code=200, _json={})

    async def aclose(self) -> None:
        return None
