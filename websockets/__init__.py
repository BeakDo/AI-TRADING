"""Minimal websockets stub."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator


@asynccontextmanager
async def connect(url: str, extra_headers: Any = None, ping_interval: float | None = None):
    class DummyWS:
        async def send(self, data: str) -> None:
            return None

        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    yield DummyWS()
