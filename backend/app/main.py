import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import get_settings
from .db import SessionLocal, engine
from .rag.indexer import sync_index
from .routers import chat, posts, projects

settings = get_settings()
logger = logging.getLogger("uvicorn.error")


async def _sync_rag_index() -> None:
    """Background startup task: re-embed any content that changed since the
    index was last built (no-op when everything is up to date)."""
    try:
        async with SessionLocal() as session:
            stats = await sync_index(session)
        logger.info(
            "RAG index synced: %s/%s sources re-embedded (%s chunks), %s removed.",
            stats["reindexed"], stats["sources"], stats["chunks"], stats["removed"],
        )
    except Exception:
        logger.exception("RAG index sync failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sync in the background so startup isn't blocked on embedding calls.
    # The local reference keeps the task alive until shutdown.
    sync_task = asyncio.create_task(_sync_rag_index()) if settings.google_api_key else None
    yield
    if sync_task is not None and not sync_task.done():
        sync_task.cancel()


app = FastAPI(title="Tsai Cheng-Hung — Resume API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(posts.router)
app.include_router(chat.router)


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
