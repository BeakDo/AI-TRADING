"""Online adaptation helpers detecting distribution shifts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Deque

from collections import deque


@dataclass
class DriftDetector:
    window: int = 100
    threshold: float = 0.1

    def __post_init__(self) -> None:
        self._buffer: Deque[float] = deque(maxlen=self.window)

    def update(self, value: float) -> bool:
        self._buffer.append(value)
        if len(self._buffer) < self.window:
            return False
        mean = sum(self._buffer) / len(self._buffer)
        return abs(mean) > self.threshold
