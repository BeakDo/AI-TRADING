# AI Trading Platform

Scaffold for a web-based AI trading system that detects intraday surges in US equities, executes trades via the Korea Investment & Securities (KIS) OpenAPI, and continuously optimises risk and profit targets using contextual bandits and survival analysis.

## Repository layout

```
repo/
  backend/      # FastAPI application, adapters, services
  frontend/     # Next.js dashboard (TypeScript + Tailwind CSS)
  infra/        # Docker Compose definitions and environment template
  tests/        # Pytest and Playwright (placeholder) suites
```

## Backend stack

- Python 3.11+
- FastAPI, httpx, websockets, pydantic-settings
- SQLModel, PostgreSQL + TimescaleDB
- Redis for pub/sub and state fan-out
- AI modules: scikit-learn, lifelines, contextual bandit scaffolding

## Frontend stack

- Next.js 14 (app router)
- React 18, TypeScript, Tailwind CSS
- Dummy data mode for offline development

## Environment variables

Copy `infra/.env.example` to `.env` at the repository root and fill the values:

```
cp infra/.env.example .env
```

Key variables:

- `KIS_APPKEY`, `KIS_APPSECRET`: API credentials
- `KIS_ACCOUNT_NO8`, `KIS_ACCOUNT_PROD2`: account identifiers
- `KIS_IS_PAPER`: toggle paper vs live trading (default `false`)
- `POSTGRES_DSN`: SQLAlchemy DSN (default docker compose value)
- `REDIS_URL`: Redis connection string
- `ENTRY_SCORE_TH`, `TP_CHOICES`, `SL_ATR_CHOICES`, `TS_CHOICES_MIN`: strategy defaults

## Running with Docker Compose

```
cd infra
cp .env.example .env
docker compose up --build
```

Services:

- `db`: TimescaleDB for historical bars, signals and orders
- `redis`: Pub/Sub hub for real-time features
- `backend`: FastAPI server (`http://localhost:8000/api/health`)
- `frontend`: Next.js dashboard (`http://localhost:3000`)

The backend container installs Python dependencies from `backend/requirements.txt`. The frontend container performs a production build before starting.

## Local development

Install Python dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Run the API:

```
uvicorn backend.main:app --reload
```

Install frontend dependencies and run the dashboard:

```
cd frontend
npm install
npm run dev
```

The dashboard renders dummy data even if the backend is offline. When connected, configure it to use the FastAPI `/api/stream` endpoint (to be implemented) for real-time updates.

## KIS integration

The scaffold intentionally ships with placeholder constants in `backend/adapters/kis_spec.py`. Populate the TODO fields with values from the official KIS documentation (endpoints, TR_ID, fields). Until then the application automatically falls back to the paper trading adapter, preventing accidental live trades.

Consult the KIS developer portal for:

- OAuth token endpoints
- Overseas order REST API specification
- WebSocket approval key issuance
- Execution notification AES256 parameters

## Testing

Run pytest from the repository root:

```
pytest
```

Playwright E2E tests can be added under `tests/e2e/` and run via `npx playwright test` once the dashboard wiring is complete.

## Common issues

- **Token expiry**: The `KISAuthManager` refreshes tokens one minute before expiry. Ensure server clocks are synchronised.
- **WebSocket disconnects**: The KIS WS client reconnects with exponential backoff (max 60s). Inspect structured logs for repeated failures.
- **Rate limits**: REST calls use a 10-second timeout; add retry logic when integrating real endpoints.
- **Docker networking**: The backend expects the database host `db` and Redis host `redis` when running inside Compose.

## Roadmap

1. Connect real-time ingest to KIS or a market data simulator.
2. Persist bars, signals and trade events into TimescaleDB.
3. Implement the execution loop with real broker events and paper simulator parity.
4. Extend the AI optimisation modules with real labelling, model training and walk-forward evaluation.
5. Complete dashboard panels for positions, P&L, risk metrics and admin controls.
