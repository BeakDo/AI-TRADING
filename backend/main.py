"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI

from .api import routes_admin, routes_public
from .core.logging import configure_logging

configure_logging()
app = FastAPI(title="AI Trading Platform")
app.include_router(routes_public.router, prefix="/api")
app.include_router(routes_admin.router, prefix="/api/admin")
