"""Database models using SQLModel."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Bar(SQLModel, table=True):
    symbol: str = Field(primary_key=True)
    ts: datetime = Field(primary_key=True)
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float
    interval: str


class Signal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    ts: datetime
    score: float
    features: dict
    tp_pct: float
    ctx: dict


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    ts: datetime
    side: str
    type: str
    px: float
    qty: float
    status: str
    parent_signal: Optional[int] = Field(default=None, foreign_key="signal.id")


class Fill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    ts: datetime
    px: float
    qty: float
    fee: float
    slippage: float


class Position(SQLModel, table=True):
    symbol: str = Field(primary_key=True)
    ts: datetime = Field(primary_key=True)
    qty: float
    avg_px: float
    unrealized: float
    realized: float
