"""Abstract broker interface used by execution services.

The project intentionally keeps the interface slim so that both real and
simulated adapters can plug into the same execution pipeline.  All adapter
implementations must be asynchronous to allow the orchestrator to multiplex
network and market data I/O efficiently.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class Broker(ABC):
    """Common broker interface shared across live and paper trading adapters."""

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
        """Submit an order and return the broker specific payload.

        The response is intentionally left untyped because different brokers may
        expose additional metadata such as order route identifiers or warning
        codes.  Downstream code should treat the return value as an opaque
        dictionary that can be logged and later normalised.
        """

    @abstractmethod
    async def cancel(self, order_id: str) -> None:
        """Cancel the order with the provided identifier."""

    @abstractmethod
    async def positions(self) -> List[Dict[str, Any]]:
        """Return the current positions in a normalised structure."""

    @abstractmethod
    async def cash(self) -> float:
        """Return available buying power or cash balance in account currency."""

    @abstractmethod
    async def stream_orders(self, on_event: Callable[[Dict[str, Any]], None]) -> None:
        """Continuously stream order updates to the supplied callback."""
