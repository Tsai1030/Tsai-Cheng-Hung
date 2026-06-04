from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from ..config import get_settings


@lru_cache
def get_embedder() -> GoogleGenerativeAIEmbeddings:
    """Gemini embeddings, truncated to settings.embed_dim (MRL)."""
    s = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model=s.gemini_embed_model,
        google_api_key=s.google_api_key,
        output_dimensionality=s.embed_dim,
    )
