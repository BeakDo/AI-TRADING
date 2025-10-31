"""Strategy loop wiring signals, bandit decisions and order routing."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncIterator, Dict

from ..signal.surge import SurgeDetector
from .bandit import ContextualBandit
from .router import OrderRouter

logger = logging.getLogger(__name__)


class StrategyLoop:
    def __init__(
        self,
        signal_stream: AsyncIterator[Dict[str, Any]],
        router: OrderRouter,
        bandit: ContextualBandit,
        surge_detector: SurgeDetector,
    ) -> None:
        self._signal_stream = signal_stream
        self._router = router
        self._bandit = bandit
        self._surge = surge_detector
        self._running = False

    async def run(self) -> None:
        self._running = True
        async for event in self._signal_stream:
            if not self._running:
                break
            if event.get("type") != "trade":
                continue
            signal = self._surge.score(event["symbol"], event.get("features", {}))
            if not self._surge.is_entry(signal):
                continue
            arm = self._bandit.select()
            result = await self._router.submit_entry(signal.symbol, "BUY", 1, arm)
            if result:
                logger.info("Submitted order %s", result)

    async def stop(self) -> None:
        self._running = False
