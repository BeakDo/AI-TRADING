"""Minimal pydantic stub."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


class BaseModel:
    def __init__(self, **data: Any) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    def dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()
