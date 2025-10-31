"""Label generation utilities for offline/online learning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd


@dataclass
class LabelResult:
    y_hit10: int
    t_hit10: float
    t_drawdown: float


def label_trades(df: pd.DataFrame) -> List[LabelResult]:
    """Generate simple labels required by the signal and hazard models.

    The scaffold assumes ``df`` contains columns ``price`` and ``timestamp`` and
    produces synthetic labels for demonstration purposes.
    """

    results: List[LabelResult] = []
    for _, row in df.iterrows():
        y_hit10 = 1 if row.get("price", 0) > 0 else 0
        t_hit10 = float(row.get("timestamp", 0))
        t_drawdown = t_hit10 + 60
        results.append(LabelResult(y_hit10=y_hit10, t_hit10=t_hit10, t_drawdown=t_drawdown))
    return results
