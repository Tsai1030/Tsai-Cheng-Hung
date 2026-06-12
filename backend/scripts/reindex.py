"""Sync the RAG index (doc_chunks) from projects + posts + profile.

Incremental by default — only changed/new/removed sources are touched.
Pass --full to force a complete re-embed (after changing the chunker or
the embedding model).

Run from the backend/ directory:
    uv run python -m scripts.reindex [--full]
"""

import asyncio
import sys

from app.db import SessionLocal, engine
from app.rag.indexer import sync_index


async def main() -> None:
    full = "--full" in sys.argv[1:]
    async with SessionLocal() as session:
        stats = await sync_index(session, full=full)
    await engine.dispose()
    print(
        f"Index synced: {stats['reindexed']}/{stats['sources']} sources re-embedded "
        f"({stats['chunks']} chunks), {stats['removed']} removed."
    )


if __name__ == "__main__":
    asyncio.run(main())
