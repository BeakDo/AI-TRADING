"""Lightweight FastAPI stub for offline environments."""
from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

RouteHandler = Callable[..., Awaitable[Any]] | Callable[..., Any]


class APIRouter:
    def __init__(self) -> None:
        self.routes: Dict[Tuple[str, str], RouteHandler] = {}

    def get(self, path: str) -> Callable[[RouteHandler], RouteHandler]:
        def decorator(func: RouteHandler) -> RouteHandler:
            self.routes[("GET", path)] = func
            return func

        return decorator

    def post(self, path: str) -> Callable[[RouteHandler], RouteHandler]:
        def decorator(func: RouteHandler) -> RouteHandler:
            self.routes[("POST", path)] = func
            return func

        return decorator


class FastAPI:
    def __init__(self, *, title: str = "") -> None:
        self.title = title
        self.routes: Dict[Tuple[str, str], RouteHandler] = {}

    def include_router(self, router: APIRouter, prefix: str = "") -> None:
        for (method, path), handler in router.routes.items():
            self.routes[(method, prefix + path)] = handler


@dataclass
class _Response:
    status_code: int
    _json: Any

    def json(self) -> Any:
        return self._json


class HTTPException(Exception):
    """간단한 HTTPException 구현."""

    def __init__(self, status_code: int, detail: str | None = None) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail or ""


def _maybe_await(result: Any) -> Any:
    if asyncio.iscoroutine(result):
        return asyncio.run(result)
    return result


class TestClient:
    def __init__(self, app: FastAPI) -> None:
        self._app = app

    def get(self, path: str) -> _Response:
        handler = self._app.routes.get(("GET", path))
        if handler is None:
            return _Response(status_code=404, _json={"detail": "Not Found"})
        try:
            result = _maybe_await(handler())
        except HTTPException as exc:  # pragma: no cover - fallback 안전장치
            return _Response(status_code=exc.status_code, _json={"detail": exc.detail})
        return _Response(status_code=200, _json=result)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> _Response:
        handler = self._app.routes.get(("POST", path))
        if handler is None:
            return _Response(status_code=404, _json={"detail": "Not Found"})
        kwargs: Dict[str, Any] = {}
        if json is not None:
            params = list(inspect.signature(handler).parameters.values())
            if params:
                param = params[0]
                annotation = param.annotation
                value: Any = json
                validator = getattr(annotation, "model_validate", None)
                if callable(validator):
                    value = validator(json)
                else:
                    factory = getattr(annotation, "__call__", None)
                    try:
                        if callable(factory):
                            value = annotation(**json)  # type: ignore[arg-type]
                    except Exception:
                        value = json
                kwargs[param.name] = value
        try:
            result = handler(**kwargs) if kwargs else handler()
            result = _maybe_await(result)
        except HTTPException as exc:
            return _Response(status_code=exc.status_code, _json={"detail": exc.detail})
        return _Response(status_code=200, _json=result)


__all__ = ["APIRouter", "FastAPI", "HTTPException", "TestClient"]
