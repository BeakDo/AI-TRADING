"""KIS OpenAPI specification placeholders.

⚠️ The real endpoint URLs, TR_ID values and payload field names MUST be
provided by the developer with access to the official KIS documentation.
Leaving the constants empty forces the broker factory to use the
:class:`~backend.adapters.paper.PaperAdapter`, keeping the application safe by
preventing accidental live trading.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class KISRestSpec:
    base_url: str = ""  # TODO: Fill with KIS REST base URL.
    overseas_order_path: str = ""  # TODO: Fill with overseas order endpoint.
    overseas_cancel_path: str = ""  # TODO: Fill with overseas cancel endpoint.
    positions_path: str = ""  # TODO: Fill with overseas positions endpoint.
    cash_path: str = ""  # TODO: Fill with overseas cash endpoint.
    timeout_seconds: float = 10.0


@dataclass(frozen=True)
class KISWebSocketSpec:
    base_url: str = ""  # TODO: Fill with KIS WebSocket endpoint.
    approval_key_path: str = ""  # TODO: Fill with approval key endpoint.
    heartbeat_interval: float = 30.0


@dataclass(frozen=True)
class KISAuthSpec:
    token_url: str = ""  # TODO: Fill with OAuth token URL.
    client_id: Optional[str] = None
    scope: Optional[str] = None


REST_SPEC = KISRestSpec()
WS_SPEC = KISWebSocketSpec()
AUTH_SPEC = KISAuthSpec()
