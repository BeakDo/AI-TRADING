"""Lightweight fill simulator used by tests and paper trading."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class SimFill:
    order_id: str
    price: float
    qty: float
    fee: float
    slippage: float


class ExecutionSimulator:
    def __init__(self, spread_bps: float = 5.0, fee_per_share: float = 0.005) -> None:
        self.spread_bps = spread_bps
        self.fee_per_share = fee_per_share

    def simulate(self, symbol: str, side: str, qty: float, price: float) -> SimFill:
        slip = price * (self.spread_bps / 10_000)
        fill_price = price + slip if side.upper() == "BUY" else price - slip
        fee = qty * self.fee_per_share
        return SimFill(order_id=f"SIM-{symbol}", price=fill_price, qty=qty, fee=fee, slippage=slip)
