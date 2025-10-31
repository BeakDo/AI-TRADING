"""High level ingest service wiring sources, processors and publishers."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, Iterable, List

from .processors.aggregator import BarAggregator
from .processors.features import FeatureComputer
from .publishers.redis_pub import RedisPublisher

logger = logging.getLogger(__name__)


class IngestService:
    """Consumes raw trades and publishes aggregated features."""

    def __init__(
        self,
        redis_publisher: RedisPublisher,
        *,
        feature_lookbacks: Iterable[int] = (5, 15, 60),
        bar_intervals: Iterable[int] = (1, 60),
    ) -> None:
        self._publisher = redis_publisher
        self._feature_comp = FeatureComputer(feature_lookbacks)
        self._aggregator = BarAggregator(bar_intervals)

    async def handle_trade(self, event: Dict[str, Any]) -> None:
        symbol = event.get("symbol", "UNKNOWN")
        price = float(event.get("price", 0.0))
        volume = float(event.get("volume", 0.0))
        ts = float(event.get("ts", 0.0))
        features = self._feature_comp.update(symbol, price, volume)
        await self._aggregator.process_trade(symbol, price, volume, ts)
        bars = await self._aggregator.get_bars()
        payload = {
            "type": "trade",
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "ts": ts,
            "features": features,
            "bars": [bar.__dict__ for bar in bars],
        }
        await self._publisher.publish(payload)
