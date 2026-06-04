from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Runtime DB connection used by FastAPI (asyncpg driver).
    # Use the Supabase Session pooler (port 5432) or a direct connection.
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    # Direct connection used by Alembic migrations (Supabase "Direct connection").
    # Leave blank to fall back to database_url.
    direct_url: str = ""

    # Comma-separated list of allowed CORS origins (the frontend).
    cors_origins: str = "http://localhost:4100"

    # Bearer token guarding admin write endpoints (used from Stage A). Blank = disabled.
    admin_token: str = ""

    environment: str = "development"

    # --- RAG assistant (Stage 5) ---
    google_api_key: str = ""
    gemini_chat_model: str = "gemini-3.5-flash"
    gemini_embed_model: str = "gemini-embedding-2"
    embed_dim: int = 768

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
