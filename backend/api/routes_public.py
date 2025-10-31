"""Public FastAPI routes exposing health and read-only strategy state."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter

from ..core.settings import settings

router = APIRouter()


@router.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok"}


@router.get("/signals/recent")
async def recent_signals(limit: int = 100) -> Dict[str, Any]:
    dummy = [
        {
            "symbol": "AAPL",
            "score": 0.72,
            "tp_pct": 0.05,
            "features": {"ret_5s": 0.01, "vol_spike": 4.0},
        }
        for _ in range(min(limit, 5))
    ]
    return {"signals": dummy}


@router.get("/positions")
async def positions() -> Dict[str, Any]:
    return {"positions": []}


@router.get("/orders")
async def orders() -> Dict[str, Any]:
    return {"orders": []}


@router.get("/pnl/daily")
async def pnl() -> Dict[str, Any]:
    return {"pnl": 0.0}
