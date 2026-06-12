"""Incremental RAG index sync.

Keeps doc_chunks in step with projects + posts + profile by hashing each
source's full text: unchanged sources are left alone (no re-embedding),
changed/new sources are re-chunked and re-embedded, and sources that
disappeared (deleted or unpublished) have their chunks removed.

Called automatically after seeding (scripts.seed), on app startup
(app.main), and manually via scripts.reindex.
"""

import asyncio
import hashlib

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DocChunk, Post, Project
from .chunk import chunk_text
from .embeddings import get_embedder
from .profile import PROFILE, PROFILE_TITLE

LANGS = ("en", "zh")

# A source is one (type, id, lang) document; its key identifies it in doc_chunks.
SourceKey = tuple[str, int | None, str]


def _pick(obj, base: str, lang: str) -> str:
    return getattr(obj, f"{base}_{lang}", "") or ""


def build_sources(projects: list[Project], posts: list[Post]) -> list[dict]:
    """Each source: {key, url, title, text, hash}."""
    sources: list[dict] = []

    def add(stype: str, sid: int | None, lang: str, url: str, title: str, text: str) -> None:
        sources.append(
            {
                "key": (stype, sid, lang),
                "url": url,
                "title": title,
                "text": text,
                "hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )

    for p in projects:
        for lang in LANGS:
            title = _pick(p, "title", lang)
            text = "\n\n".join(x for x in [title, _pick(p, "summary", lang), _pick(p, "body", lang)] if x)
            add("project", p.id, lang, f"/projects/{p.slug}", title, text)
    for p in posts:
        for lang in LANGS:
            title = _pick(p, "title", lang)
            text = "\n\n".join(x for x in [title, _pick(p, "excerpt", lang), _pick(p, "body", lang)] if x)
            add("post", p.id, lang, f"/blog/{p.slug}", title, text)
    for lang in LANGS:
        add("profile", None, lang, "/", PROFILE_TITLE[lang], PROFILE[lang])
    return sources


def _key_clause(key: SourceKey):
    stype, sid, lang = key
    return and_(
        DocChunk.source_type == stype,
        DocChunk.source_id.is_(None) if sid is None else DocChunk.source_id == sid,
        DocChunk.lang == lang,
    )


async def sync_index(session: AsyncSession, full: bool = False) -> dict:
    """Bring doc_chunks in sync with current content. Returns stats.

    full=True re-embeds everything regardless of hashes (use after changing
    the chunker or the embedding model).
    """
    projects = (
        await session.execute(select(Project).where(Project.published.is_(True)))
    ).scalars().all()
    posts = (
        await session.execute(select(Post).where(Post.published.is_(True)))
    ).scalars().all()
    sources = build_sources(list(projects), list(posts))

    indexed = {
        (stype, sid, lang): chash
        for stype, sid, lang, chash in (
            await session.execute(
                select(
                    DocChunk.source_type, DocChunk.source_id, DocChunk.lang, DocChunk.content_hash
                ).distinct()
            )
        ).all()
    }

    changed = [s for s in sources if full or indexed.get(s["key"]) != s["hash"]]
    orphans = set(indexed) - {s["key"] for s in sources}
    stale_keys = [s["key"] for s in changed] + list(orphans)

    if stale_keys:
        await session.execute(delete(DocChunk).where(or_(*map(_key_clause, stale_keys))))

    records: list[tuple[dict, int, str]] = []  # (source, chunk_index, content)
    for s in changed:
        for i, ch in enumerate(chunk_text(s["text"])):
            records.append((s, i, ch))

    if records:
        embedder = get_embedder()
        vectors = await asyncio.to_thread(embedder.embed_documents, [r[2] for r in records])
        session.add_all(
            DocChunk(
                source_type=s["key"][0],
                source_id=s["key"][1],
                lang=s["key"][2],
                url=s["url"],
                title=s["title"],
                chunk_index=i,
                content=content,
                embedding=vec,
                content_hash=s["hash"],
            )
            for (s, i, content), vec in zip(records, vectors)
        )

    await session.commit()
    return {
        "sources": len(sources),
        "reindexed": len(changed),
        "removed": len(orphans),
        "chunks": len(records),
    }
