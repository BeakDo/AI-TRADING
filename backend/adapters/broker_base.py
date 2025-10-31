"""실행 서비스에서 사용하는 추상 브로커 인터페이스.

이 프로젝트는 실계좌와 시뮬레이터 어댑터 모두가 동일한 실행 파이프라인에
연결될 수 있도록 인터페이스를 의도적으로 간결하게 유지한다. 모든
어댑터 구현은 오케스트레이터가 네트워크와 시세 I/O를 효율적으로
멀티플렉싱할 수 있도록 비동기로 작성되어야 한다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class Broker(ABC):
    """실계좌/모의 어댑터가 공통으로 구현해야 하는 브로커 인터페이스."""

    @abstractmethod
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
        """주문을 제출하고 브로커 고유 응답 페이로드를 반환한다.

        브로커마다 주문 경로 식별자나 경고 코드처럼 서로 다른 메타데이터를
        제공할 수 있으므로 응답 타입을 고정하지 않았다. 후속 코드는 응답을
        로깅하거나 사후 정규화할 수 있는 불투명한 사전으로 취급해야 한다.
        """

    @abstractmethod
    async def cancel(self, order_id: str) -> None:
        """지정된 식별자의 주문을 취소한다."""

    @abstractmethod
    async def positions(self) -> List[Dict[str, Any]]:
        """현재 포지션을 정규화된 구조로 반환한다."""

    @abstractmethod
    async def cash(self) -> float:
        """계좌 통화 기준의 사용 가능한 매수 여력 또는 현금 잔고를 반환한다."""

    @abstractmethod
    async def stream_orders(self, on_event: Callable[[Dict[str, Any]], None]) -> None:
        """주문 업데이트를 지정된 콜백으로 지속적으로 전달한다."""
