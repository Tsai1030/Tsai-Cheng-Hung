from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import get_settings
from .db import engine

settings = get_settings()

app = FastAPI(title="Tsai Cheng-Hung — Resume API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
async def health_db() -> dict[str, str]:
    """Verifies the backend can reach Supabase Postgres."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "db": str(exc)}


# Stage 1 will register routers, e.g.:
#   from .routers import projects, posts
#   app.include_router(projects.router)
#   app.include_router(posts.router)
