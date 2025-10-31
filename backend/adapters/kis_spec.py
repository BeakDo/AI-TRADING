"""KIS OpenAPI 명세 자리표시자 모음.

⚠️ 실제 엔드포인트 URL, TR_ID, 페이로드 필드 이름은 반드시 KIS 공식
문서를 확인한 개발자가 채워 넣어야 한다. 상수를 비워 두면 브로커 팩토리가
:class:`~backend.adapters.paper.PaperAdapter`를 사용하도록 강제하여, 실수로
실계좌 주문이 나가는 일을 막는다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class KISRestSpec:
    base_url: str = ""  # TODO: KIS REST 기본 URL을 입력한다.
    overseas_order_path: str = ""  # TODO: 해외 주문 엔드포인트를 입력한다.
    overseas_cancel_path: str = ""  # TODO: 해외 정정/취소 엔드포인트를 입력한다.
    positions_path: str = ""  # TODO: 해외 잔고 조회 엔드포인트를 입력한다.
    cash_path: str = ""  # TODO: 해외 현금 잔고 엔드포인트를 입력한다.
    timeout_seconds: float = 10.0


@dataclass(frozen=True)
class KISWebSocketSpec:
    base_url: str = ""  # TODO: KIS WebSocket 엔드포인트를 입력한다.
    approval_key_path: str = ""  # TODO: 승인 키 발급 엔드포인트를 입력한다.
    heartbeat_interval: float = 30.0


@dataclass(frozen=True)
class KISAuthSpec:
    token_url: str = ""  # TODO: OAuth 토큰 발급 URL을 입력한다.
    client_id: Optional[str] = None
    scope: Optional[str] = None


REST_SPEC = KISRestSpec()
WS_SPEC = KISWebSocketSpec()
AUTH_SPEC = KISAuthSpec()
