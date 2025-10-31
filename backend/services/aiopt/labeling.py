"""오프라인/온라인 학습용 라벨 생성 유틸리티."""
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
    """신호/해저드 모델에 필요한 단순 라벨을 생성한다.

    이 스캐폴드는 ``df``가 ``price``와 ``timestamp`` 컬럼을 포함한다고 가정하며
    데모 목적의 합성 라벨을 생성한다.
    """

    results: List[LabelResult] = []
    for _, row in df.iterrows():
        y_hit10 = 1 if row.get("price", 0) > 0 else 0
        t_hit10 = float(row.get("timestamp", 0))
        t_drawdown = t_hit10 + 60
        results.append(LabelResult(y_hit10=y_hit10, t_hit10=t_hit10, t_drawdown=t_drawdown))
    return results
