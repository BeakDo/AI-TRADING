"""밴딧 정책을 위한 보상 계산 유틸리티."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradeOutcome:
    realized: float
    unrealized: float
    fees: float
    slippage: float
    holding_time: float


def compute_reward(outcome: TradeOutcome) -> float:
    pnl = outcome.realized + outcome.unrealized - outcome.fees - outcome.slippage
    penalty = outcome.holding_time / 3600.0
    return pnl - penalty
