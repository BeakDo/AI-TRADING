"""신호 엔진에서 사용하는 피처 엔지니어링 유틸리티."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict, Iterable


class FeatureComputer:
    """수익률·거래량 기반 피처를 위한 롤링 윈도우를 관리한다."""

    def __init__(self, lookbacks: Iterable[int]) -> None:
        self._lookbacks = list(lookbacks)
        self._price_history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=max(self._lookbacks)))
        self._volume_history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=120))

    def update(self, symbol: str, price: float, volume: float) -> Dict[str, float]:
        prices = self._price_history[symbol]
        prices.append(price)
        vols = self._volume_history[symbol]
        vols.append(volume)
        features: Dict[str, float] = {}
        for lookback in self._lookbacks:
            if len(prices) >= lookback:
                ref = prices[-lookback]
                if ref:
                    features[f"ret_{lookback}s"] = (price - ref) / ref
        if vols:
            avg_vol = sum(vols) / len(vols)
            if avg_vol > 0:
                features["vol_spike"] = volume / avg_vol
        return features

    @staticmethod
    def zscore(value: float, mean: float, std: float) -> float:
        if std == 0:
            return 0.0
        return (value - mean) / std
