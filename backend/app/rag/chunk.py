import re

_IMG = re.compile(r"!\[[^\]]*\]\([^)]*\)")  # markdown images


def strip_media(text: str) -> str:
    """Drop markdown image embeds (they carry no useful text for retrieval)."""
    return _IMG.sub("", text)


def chunk_text(text: str, max_chars: int = 900, overlap_paras: int = 1) -> list[str]:
    """Paragraph-aware chunker: greedily pack paragraphs up to max_chars,
    carrying `overlap_paras` paragraphs into the next chunk for continuity."""
    text = strip_media(text).strip()
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for p in paras:
        if cur and cur_len + len(p) > max_chars:
            chunks.append("\n\n".join(cur))
            cur = cur[-overlap_paras:] if overlap_paras else []
            cur_len = sum(len(x) for x in cur)
        cur.append(p)
        cur_len += len(p)
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks
