"""간단한 SQLModel 스텁."""
from __future__ import annotations

from typing import Any


def Field(default: Any = None, primary_key: bool = False, foreign_key: str | None = None):
    return default


class SQLModel:
    pass
