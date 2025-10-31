"""간단한 pydantic 스텁."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


class BaseModel:
    def __init__(self, **data: Any) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    def dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def model_dump(self) -> Dict[str, Any]:
        return self.dict()

    @classmethod
    def model_validate(cls, data: Dict[str, Any]) -> "BaseModel":
        return cls(**data)


def Field(default: Any, description: str | None = None) -> Any:  # noqa: D401 - 단순 스텁
    """pydantic.Field 대체."""

    return default


__all__ = ["BaseModel", "Field"]
