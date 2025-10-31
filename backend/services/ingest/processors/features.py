"""Feature engineering utilities used by the signal engine."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict, Iterable


class FeatureComputer:
    """Tracks rolling windows for return and volume based features."""

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
