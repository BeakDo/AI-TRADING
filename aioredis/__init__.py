"""Minimal aioredis stub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Redis:
    async def publish(self, channel: str, message: str) -> None:
        return None

    async def close(self) -> None:
        return None


async def from_url(url: str, *, encoding: str = "utf-8", decode_responses: bool = True) -> Redis:
    return Redis()
