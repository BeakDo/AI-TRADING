"""KIS 해외 주식 거래 엔드포인트를 감싸는 HTTP 클라이언트 래퍼.

모든 메서드는 :class:`~backend.adapters.broker_base.Broker` 인터페이스를
준수하며 명세 상수가 아직 설정되지 않은 경우 :class:`PaperAdapter`로
안전하게 폴백한다.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from .broker_base import Broker
from .kis_spec import REST_SPEC

logger = logging.getLogger(__name__)


class KISOverseasBroker(Broker):
    """KIS 해외 거래 엔드포인트를 감싸는 최소한의 비동기 래퍼."""

    def __init__(
        self,
        *,
        app_key: str,
        app_secret: str,
        account_no8: str,
        account_prod2: str,
        is_paper: bool,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        if not REST_SPEC.base_url:
            raise RuntimeError("KIS specification incomplete; use PaperAdapter instead.")
        self._app_key = app_key
        self._app_secret = app_secret
        self._account_no8 = account_no8
        self._account_prod2 = account_prod2
        self._is_paper = is_paper
        self._client = client or httpx.AsyncClient(base_url=REST_SPEC.base_url, timeout=REST_SPEC.timeout_seconds)

    async def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        order_type: str = "MKT",
        limit_price: Optional[float] = None,
        tif: str = "DAY",
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "order_type": order_type,
            "limit_price": limit_price,
            "tif": tif,
            "meta": meta or {},
        }
        logger.info("Submitting KIS order %s", payload)
        response = await self._client.post(REST_SPEC.overseas_order_path, json=payload)
        response.raise_for_status()
        return response.json()

    async def cancel(self, order_id: str) -> None:
        logger.info("Cancelling KIS order %s", order_id)
        response = await self._client.post(REST_SPEC.overseas_cancel_path, json={"order_id": order_id})
        response.raise_for_status()

    async def positions(self) -> List[Dict[str, Any]]:
        response = await self._client.get(REST_SPEC.positions_path)
        response.raise_for_status()
        return response.json().get("positions", [])

    async def cash(self) -> float:
        response = await self._client.get(REST_SPEC.cash_path)
        response.raise_for_status()
        data = response.json()
        return float(data.get("cash", 0.0))

    async def stream_orders(self, on_event: Any) -> None:  # pragma: no cover - WS 필요
        raise NotImplementedError("KIS order streaming is not implemented in the scaffold")
