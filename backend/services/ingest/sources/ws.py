"""WebSocket ingestion utilities bridging adapters and processors."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, Iterable

logger = logging.getLogger(__name__)


class WebSocketIngestor:
    """Wraps a :class:`MarketDataFeed` and funnels messages to processors."""

    def __init__(
        self,
        feed_factory: Callable[[Callable[[Dict[str, Any]], Awaitable[None]]], Awaitable[Any]],
        processors: Iterable[Callable[[Dict[str, Any]], Awaitable[None]]],
    ) -> None:
        self._feed_factory = feed_factory
        self._processors = list(processors)
        self._should_run = True

    async def start(self) -> None:
        async def on_event(event: Dict[str, Any]) -> None:
            for processor in self._processors:
                await processor(event)

        feed = await self._feed_factory(on_event)
        while self._should_run:
            try:
                await feed.run()
            except Exception as exc:  # pragma: no cover
                logger.error("Ingest feed error: %s", exc)
                await asyncio.sleep(1)

    async def stop(self) -> None:
        self._should_run = False
