"""Rebuild the RAG index (doc_chunks) from projects + posts + profile.

Run from the backend/ directory:
    uv run python -m scripts.reindex
"""

import asyncio

from sqlalchemy import delete, select

from app.db import SessionLocal, engine
from app.models import DocChunk, Post, Project
from app.rag.chunk import chunk_text
from app.rag.embeddings import get_embedder
from app.rag.profile import PROFILE, PROFILE_TITLE

LANGS = ("en", "zh")


def _pick(obj, base: str, lang: str) -> str:
    return getattr(obj, f"{base}_{lang}", "") or ""


def build_sources(projects: list[Project], posts: list[Post]) -> list[tuple]:
    """Each source: (source_type, source_id, lang, url, title, text)."""
    sources: list[tuple] = []
    for p in projects:
        for lang in LANGS:
            title = _pick(p, "title", lang)
            text = "\n\n".join(x for x in [title, _pick(p, "summary", lang), _pick(p, "body", lang)] if x)
            sources.append(("project", p.id, lang, f"/projects/{p.slug}", title, text))
    for p in posts:
        for lang in LANGS:
            title = _pick(p, "title", lang)
            text = "\n\n".join(x for x in [title, _pick(p, "excerpt", lang), _pick(p, "body", lang)] if x)
            sources.append(("post", p.id, lang, f"/blog/{p.slug}", title, text))
    for lang in LANGS:
        sources.append(("profile", None, lang, "/", PROFILE_TITLE[lang], PROFILE[lang]))
    return sources


async def main() -> None:
    embedder = get_embedder()
    async with SessionLocal() as session:
        projects = (
            await session.execute(select(Project).where(Project.published.is_(True)))
        ).scalars().all()
        posts = (
            await session.execute(select(Post).where(Post.published.is_(True)))
        ).scalars().all()

        sources = build_sources(list(projects), list(posts))

        # (source_type, source_id, lang, url, title, chunk_index, content)
        records: list[tuple] = []
        for stype, sid, lang, url, title, text in sources:
            for i, ch in enumerate(chunk_text(text)):
                records.append((stype, sid, lang, url, title, i, ch))

        # Embed all chunk contents (batched by the client).
        vectors = embedder.embed_documents([r[6] for r in records])

        await session.execute(delete(DocChunk))
        session.add_all(
            DocChunk(
                source_type=r[0],
                source_id=r[1],
                lang=r[2],
                url=r[3],
                title=r[4],
                chunk_index=r[5],
                content=r[6],
                embedding=vec,
            )
            for r, vec in zip(records, vectors)
        )
        await session.commit()

    await engine.dispose()
    print(f"Indexed {len(records)} chunks from {len(sources)} sources.")


if __name__ == "__main__":
    asyncio.run(main())
