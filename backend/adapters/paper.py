"""Paper trading adapter used for simulations and tests.

The adapter follows the :class:`~backend.adapters.broker_base.Broker` interface
and keeps all state in-memory, allowing the execution loop to run without
external dependencies.  It implements a simple matching model that mimics
market and limit order behaviour using a synthetic order book updated through
:class:`PaperMarketDataFeed` events.
"""
from __future__ import annotations

import asyncio
import itertools
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .broker_base import Broker

logger = logging.getLogger(__name__)


@dataclass
class PaperOrder:
    order_id: str
    symbol: str
    side: str
    qty: float
    remaining: float
    order_type: str
    limit_price: Optional[float]
    tif: str
    ts: float = field(default_factory=time.time)


class PaperMarketDataFeed:
    """Simple market data feed used to approximate fills for market orders."""

    def __init__(self) -> None:
        self._last_trade: Dict[str, float] = {}
        self._spread: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def update(self, symbol: str, price: float, spread: float) -> None:
        async with self._lock:
            self._last_trade[symbol] = price
            self._spread[symbol] = spread

    async def quote(self, symbol: str) -> tuple[float, float]:
        async with self._lock:
            price = self._last_trade.get(symbol, 100.0)
            spread = self._spread.get(symbol, 0.05)
            return price, spread


class PaperAdapter(Broker):
    """In-memory broker adapter implementing optimistic fill rules."""

    def __init__(self, data_feed: Optional[PaperMarketDataFeed] = None) -> None:
        self._orders: Dict[str, PaperOrder] = {}
        self._positions: Dict[str, float] = {}
        self._avg_price: Dict[str, float] = {}
        self._cash: float = 100_000.0
        self._id_counter = itertools.count(1)
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._data_feed = data_feed or PaperMarketDataFeed()
        self._lock = asyncio.Lock()

    async def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        order_type: str = "MKT",
        limit_price: Optional[float] = None,
        tif: str = "DAY",
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        order_id = f"PAPER-{next(self._id_counter)}"
        order = PaperOrder(order_id, symbol, side, qty, qty, order_type, limit_price, tif)
        async with self._lock:
            self._orders[order_id] = order
        asyncio.create_task(self._attempt_fill(order))
        payload = {"order_id": order_id, "status": "accepted", "meta": meta or {}}
        logger.debug("Paper order accepted %s", payload)
        return payload

    async def _attempt_fill(self, order: PaperOrder) -> None:
        await asyncio.sleep(random.uniform(0.05, 0.2))
        fill_price = await self._determine_fill_price(order)
        async with self._lock:
            order.remaining = 0
            self._orders.pop(order.order_id, None)
            qty = order.qty if order.side.upper() == "BUY" else -order.qty
            position = self._positions.get(order.symbol, 0.0)
            new_position = position + qty
            self._positions[order.symbol] = new_position
            self._avg_price[order.symbol] = fill_price
            cash_delta = -fill_price * qty
            self._cash += cash_delta
        event = {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "qty": order.qty,
            "price": fill_price,
            "status": "filled",
        }
        for callback in self._callbacks:
            callback(event)

    async def _determine_fill_price(self, order: PaperOrder) -> float:
        price, spread = await self._data_feed.quote(order.symbol)
        if order.order_type.upper() == "MKT" or order.limit_price is None:
            return price + (spread / 2 if order.side.upper() == "BUY" else -spread / 2)
        if order.side.upper() == "BUY":
            return min(order.limit_price, price)
        return max(order.limit_price, price)

    async def cancel(self, order_id: str) -> None:
        async with self._lock:
            order = self._orders.pop(order_id, None)
        if order:
            logger.debug("Paper order cancelled %s", order_id)

    async def positions(self) -> List[Dict[str, Any]]:
        async with self._lock:
            return [
                {
                    "symbol": symbol,
                    "qty": qty,
                    "avg_price": self._avg_price.get(symbol, 0.0),
                }
                for symbol, qty in self._positions.items()
            ]

    async def cash(self) -> float:
        async with self._lock:
            return self._cash

    async def stream_orders(self, on_event: Callable[[Dict[str, Any]], None]) -> None:
        self._callbacks.append(on_event)
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            self._callbacks.remove(on_event)
