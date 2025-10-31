"""초기 급등 탐지 휴리스틱 구현."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class SurgeSignal:
    symbol: str
    score: float
    features: Dict[str, float]


class SurgeDetector:
    """수익률과 거래량을 기반으로 0~1 사이의 급등 점수를 계산한다."""

    def __init__(self, entry_threshold: float = 0.6, vol_spike_threshold: float = 3.0) -> None:
        self.entry_threshold = entry_threshold
        self.vol_spike_threshold = vol_spike_threshold

    def score(self, symbol: str, features: Dict[str, float]) -> SurgeSignal:
        ret_5 = max(0.0, features.get("ret_5s", 0.0))
        ret_15 = max(0.0, features.get("ret_15s", 0.0))
        vol_spike = features.get("vol_spike", 0.0)
        z_ret = min(1.0, ret_5 * 20 + ret_15 * 10)
        z_vol = max(0.0, min(1.0, (vol_spike / max(self.vol_spike_threshold, 1e-9)) - 1.0))
        score = max(0.0, min(1.0, 0.7 * z_ret + 0.3 * z_vol))
        return SurgeSignal(symbol=symbol, score=score, features=features)

    def is_entry(self, signal: SurgeSignal) -> bool:
        return signal.score >= self.entry_threshold and signal.features.get("vol_spike", 0.0) >= self.vol_spike_threshold
