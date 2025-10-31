"""Risk guardrails protecting the strategy from runaway losses."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskState:
    daily_loss: float = 0.0
    positions: int = 0
    trading_enabled: bool = True


class RiskManager:
    def __init__(self, max_drawdown: float, max_positions: int) -> None:
        self.state = RiskState()
        self.max_drawdown = max_drawdown
        self.max_positions = max_positions
        self._lock = asyncio.Lock()

    async def register_fill(self, pnl: float) -> None:
        async with self._lock:
            self.state.daily_loss = min(0.0, self.state.daily_loss + pnl)
            logger.debug("Updated daily loss: %s", self.state.daily_loss)
            if abs(self.state.daily_loss) >= self.max_drawdown:
                self.state.trading_enabled = False
                logger.warning("Trading disabled due to drawdown")

    async def register_position_change(self, delta: int) -> None:
        async with self._lock:
            self.state.positions += delta
            logger.debug("Open positions: %s", self.state.positions)

    async def can_open_new(self) -> bool:
        async with self._lock:
            return (
                self.state.trading_enabled
                and abs(self.state.daily_loss) < self.max_drawdown
                and self.state.positions < self.max_positions
            )

    async def toggle_trading(self, enabled: bool) -> None:
        async with self._lock:
            self.state.trading_enabled = enabled
            logger.info("Trading toggled: %s", enabled)

    async def snapshot(self) -> RiskState:
        async with self._lock:
            return RiskState(
                daily_loss=self.state.daily_loss,
                positions=self.state.positions,
                trading_enabled=self.state.trading_enabled,
            )
