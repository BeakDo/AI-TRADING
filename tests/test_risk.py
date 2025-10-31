import asyncio

from backend.services.exec.risk import RiskManager


def test_risk_drawdown_blocks():
    async def scenario():
        risk = RiskManager(max_drawdown=100, max_positions=3)
        assert await risk.can_open_new()
        await risk.register_fill(-150)
        assert not await risk.can_open_new()

    asyncio.run(scenario())
