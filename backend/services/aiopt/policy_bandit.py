"""Wrapper utilities connecting AI policy with the execution bandit."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..exec.bandit import BanditArm, ContextualBandit


@dataclass
class PolicyDecision:
    arm: BanditArm
    probability: float


class PolicyController:
    def __init__(self, bandit: ContextualBandit) -> None:
        self._bandit = bandit

    def choose(self) -> PolicyDecision:
        arm = self._bandit.select()
        return PolicyDecision(arm=arm, probability=1.0)

    def update(self, arm: BanditArm, reward: float) -> None:
        self._bandit.update(arm, reward)
