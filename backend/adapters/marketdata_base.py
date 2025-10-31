"""인제스트 서비스에서 사용하는 스트리밍 시세 인터페이스 추상 클래스."""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict


class MarketDataFeed(ABC):
    """WebSocket 피드가 구현해야 하는 추상 인터페이스."""

    @abstractmethod
    async def run(self) -> None:
        """피드를 시작하고 취소될 때까지 이벤트를 스트리밍한다."""

    @abstractmethod
    async def stop(self) -> None:
        """피드를 정상적으로 중지한다."""


class CallbackMarketDataFeed(MarketDataFeed):
    """콜백으로 원시 이벤트를 전달하는 유틸리티 피드."""

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
