"""브로커 상호작용을 조율하는 주문 라우터."""
from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional

from ...adapters.broker_base import Broker
from .bandit import BanditArm
from .risk import RiskManager

logger = logging.getLogger(__name__)


class OrderRouter:
    def __init__(self, broker: Broker, risk: RiskManager) -> None:
        self._broker = broker
        self._risk = risk

    async def submit_entry(self, symbol: str, side: str, qty: float, arm: BanditArm) -> Optional[Dict[str, any]]:
        if not await self._risk.can_open_new():
            logger.info("Risk prevented new position")
            return None
        payload = await self._broker.place_order(symbol, side, qty, meta={"tp": arm.tp, "sl_atr": arm.sl_atr, "tstop": arm.tstop_min})
        await self._risk.register_position_change(1)
        return payload

    async def submit_exit(self, order_id: str) -> None:
        await self._broker.cancel(order_id)
        await self._risk.register_position_change(-1)
