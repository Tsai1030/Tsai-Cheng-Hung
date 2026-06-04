# Resume Backend (FastAPI + SQLAlchemy)

Python API for the résumé / blog / projects site. Owns all DB access + (later) the RAG assistant.
Managed with **uv**.

## Setup

```bash
cd backend
cp .env.example .env          # then fill in your Supabase connection strings
uv sync                       # creates .venv and installs deps (writes uv.lock)
```

## Run (local, port 8001)

```bash
uv run uvicorn app.main:app --reload --port 8001
```

- Health:    http://localhost:8001/health      → `{"status":"ok"}`
- DB health:  http://localhost:8001/health/db   → `{"status":"ok","db":"connected"}` once `.env` is set
- Swagger:   http://localhost:8001/docs

## Migrations (Alembic) — from Stage 1

```bash
uv run alembic revision --autogenerate -m "create projects and posts"
uv run alembic upgrade head
```

Alembic reads `DIRECT_URL` (falls back to `DATABASE_URL`) from `.env`.
