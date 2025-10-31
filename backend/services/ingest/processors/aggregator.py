"""Simple in-memory OHLCV aggregation utilities."""
from __future__ import annotations

import asyncio
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Tuple


@dataclass
class Bar:
    symbol: str
    ts: float
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float


class BarAggregator:
    """틱 데이터를 다양한 구간의 OHLCV 바로 집계한다."""

    def __init__(self, intervals: Iterable[int]) -> None:
        self._intervals = list(intervals)
        self._buckets: Dict[Tuple[str, int], List[float]] = defaultdict(list)
        self._volume: Dict[Tuple[str, int], float] = defaultdict(float)
        self._last_emit: Dict[Tuple[str, int], float] = defaultdict(time.time)
        self._queue: Deque[Bar] = deque()
        self._lock = asyncio.Lock()

    async def process_trade(self, symbol: str, price: float, volume: float, ts: float) -> None:
        async with self._lock:
            for interval in self._intervals:
                key = (symbol, interval)
                self._buckets[key].append(price)
                self._volume[key] += volume
                last_emit = self._last_emit[key]
                if ts - last_emit >= interval:
                    prices = self._buckets.pop(key, [])
                    total_volume = self._volume.pop(key, 0.0)
                    if not prices:
                        continue
                    bar = Bar(
                        symbol=symbol,
                        ts=ts,
                        interval=f"{interval}s",
                        open=prices[0],
                        high=max(prices),
                        low=min(prices),
                        close=prices[-1],
                        volume=total_volume,
                        vwap=statistics.fmean(prices),
                    )
                    self._queue.append(bar)
                    self._last_emit[key] = ts

    async def get_bars(self) -> List[Bar]:
        async with self._lock:
            bars = list(self._queue)
            self._queue.clear()
            return bars
