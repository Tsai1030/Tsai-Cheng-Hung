import asyncio

from sqlalchemy import text

from ..db import SessionLocal
from .embeddings import get_embedder


async def retrieve(query: str, lang: str, k: int = 6) -> tuple[str, list[dict], list[dict]]:
    """Embed the query and pull the top-k chunks (same language) from pgvector.

    Returns (context_string, sources, docs).
    """
    embedder = get_embedder()
    qv = await asyncio.to_thread(embedder.embed_query, query)

    sql = text(
        "select title, url, content, 1 - (embedding <=> cast(:v as vector)) as score "
        "from doc_chunks where lang = :lang "
        "order by embedding <=> cast(:v as vector) limit :k"
    )
    async with SessionLocal() as session:
        rows = (await session.execute(sql, {"v": str(qv), "lang": lang, "k": k})).all()

    docs = [{"title": t, "url": u, "content": c, "score": float(s)} for t, u, c, s in rows]

    seen: set[str] = set()
    sources: list[dict] = []
    for d in docs:
        if d["url"] not in seen:
            seen.add(d["url"])
            sources.append({"title": d["title"], "url": d["url"]})

    context = "\n\n".join(f"[{d['title']}]({d['url']})\n{d['content']}" for d in docs)
    return context, sources, docs
