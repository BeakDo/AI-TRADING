from __future__ import annotations

from . import FastAPI, TestClient as _TestClient


class TestClient(_TestClient):
    """`from fastapi.testclient import TestClient` 호환성을 위한 래퍼."""

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
