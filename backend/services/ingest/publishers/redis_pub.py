"""집계된 시세와 피처를 발행하는 Redis 퍼블리셔."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

import aioredis

logger = logging.getLogger(__name__)


class RedisPublisher:
    def __init__(self, redis_url: str, channel: str) -> None:
        self._redis_url = redis_url
        self._channel = channel
        self._redis: aioredis.Redis | None = None

    async def start(self) -> None:
        if self._redis is None:
            self._redis = await aioredis.from_url(self._redis_url, encoding="utf-8", decode_responses=True)

    async def stop(self) -> None:
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    async def publish(self, payload: Dict[str, Any]) -> None:
        if self._redis is None:
            await self.start()
        assert self._redis is not None
        await self._redis.publish(self._channel, json.dumps(payload))
