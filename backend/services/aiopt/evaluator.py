"""워크포워드 평가 헬퍼."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np


@dataclass
class EvaluationResult:
    sharpe: float
    win_rate: float
    avg_hold: float


def evaluate(pnls: Iterable[float], holds: Iterable[float]) -> EvaluationResult:
    pnl_array = np.array(list(pnls))
    hold_array = np.array(list(holds))
    sharpe = pnl_array.mean() / (pnl_array.std() + 1e-9)
    win_rate = float((pnl_array > 0).mean()) if len(pnl_array) else 0.0
    avg_hold = float(hold_array.mean()) if len(hold_array) else 0.0
    return EvaluationResult(sharpe=sharpe, win_rate=win_rate, avg_hold=avg_hold)
