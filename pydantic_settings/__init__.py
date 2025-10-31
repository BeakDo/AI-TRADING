from __future__ import annotations

import os
from typing import Any, Dict


class SettingsConfigDict(dict):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


class BaseSettings:
    model_config: SettingsConfigDict = SettingsConfigDict()

    def __init__(self, **overrides: Any) -> None:
        for name, value in self.__class__.__dict__.items():
            if name.startswith("_"):
                continue
            if callable(value):
                continue
            env_value = os.getenv(name)
            if env_value is not None:
                setattr(self, name, self._coerce(value, env_value))
            elif name in overrides:
                setattr(self, name, overrides[name])
            else:
                setattr(self, name, value)

    def _coerce(self, default: Any, value: str) -> Any:
        if isinstance(default, bool):
            return value.lower() in {"1", "true", "yes"}
        if isinstance(default, int):
            try:
                return int(value)
            except ValueError:
                return default
        if isinstance(default, float):
            try:
                return float(value)
            except ValueError:
                return default
        if isinstance(default, list):
            return [self._coerce(default[0], v) for v in value.split(",") if v]
        return value
