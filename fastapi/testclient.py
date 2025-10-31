from __future__ import annotations

from . import FastAPI, TestClient as _TestClient


class TestClient(_TestClient):
    """Compatibility shim for `from fastapi.testclient import TestClient`."""

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
