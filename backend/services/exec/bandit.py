"""Contextual bandit scaffold for TP/SL/TimeStop selection."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


@dataclass
class BanditArm:
    tp: float
    sl_atr: float
    tstop_min: int
    successes: float = 1.0
    trials: float = 2.0

    def sample(self) -> float:
        return random.betavariate(self.successes, self.trials - self.successes)


class ContextualBandit:
    def __init__(
        self,
        tp_choices: Sequence[float],
        sl_choices: Sequence[float],
        tstop_choices: Sequence[int],
        epsilon: float = 0.07,
    ) -> None:
        self.epsilon = epsilon
        self.arms: List[BanditArm] = [
            BanditArm(tp=tp, sl_atr=sl, tstop_min=tstop)
            for tp in tp_choices
            for sl in sl_choices
            for tstop in tstop_choices
        ]

    def select(self) -> BanditArm:
        if random.random() < self.epsilon:
            return random.choice(self.arms)
        return max(self.arms, key=lambda arm: arm.sample())

    def update(self, arm: BanditArm, reward: float) -> None:
        success = reward > 0
        arm.successes += 1 if success else 0.1
        arm.trials += 1
        if reward < 0:
            self.epsilon = max(0.01, self.epsilon * 0.9)
        else:
            self.epsilon = min(0.2, self.epsilon * 1.05)
