"""Administrative routes for toggling trading and updating parameters."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ToggleRequest(BaseModel):
    enabled: bool


class ParamsRequest(BaseModel):
    entry_score_th: float


@router.post("/trade/enable")
async def trade_enable(req: ToggleRequest) -> Dict[str, Any]:
    return {"enabled": req.enabled}


@router.post("/params")
async def update_params(req: ParamsRequest) -> Dict[str, Any]:
    return {"entry_score_th": req.entry_score_th}
