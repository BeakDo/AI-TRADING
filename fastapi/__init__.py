"""Lightweight FastAPI stub for offline environments."""
from __future__ import annotations

import asyncio
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
        result = _maybe_await(handler())
        return _Response(status_code=200, _json=result)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> _Response:
        handler = self._app.routes.get(("POST", path))
        if handler is None:
            return _Response(status_code=404, _json={"detail": "Not Found"})
        if json is not None:
            result = handler(json)
        else:
            result = handler()
        result = _maybe_await(result)
        return _Response(status_code=200, _json=result)


__all__ = ["APIRouter", "FastAPI", "TestClient"]
