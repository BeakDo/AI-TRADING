"""Abstract interface for streaming market data used by the ingest service."""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict


class MarketDataFeed(ABC):
    """Abstract interface implemented by WebSocket feeds."""

    @abstractmethod
    async def run(self) -> None:
        """Start the feed and keep streaming events until cancelled."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop the feed gracefully."""


class CallbackMarketDataFeed(MarketDataFeed):
    """Utility feed that forwards raw events to the supplied callback."""

    def __init__(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        self._callback = callback
        self._running = False

    async def run(self) -> None:
        self._running = True
        while self._running:
            await self._callback({"type": "dummy", "price": 100.0})
            await asyncio.sleep(1)

    async def stop(self) -> None:
        self._running = False
