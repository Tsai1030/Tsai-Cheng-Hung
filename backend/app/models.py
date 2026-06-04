"""SQLAlchemy models.

projects + posts here (Stage 1). doc_chunks comes in Stage 5.
Importing this module registers all model metadata on Base for Alembic.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    title_en: Mapped[str] = mapped_column(String(200))
    title_zh: Mapped[str] = mapped_column(String(200))
    summary_en: Mapped[str] = mapped_column(Text, default="")
    summary_zh: Mapped[str] = mapped_column(Text, default="")
    body_en: Mapped[str] = mapped_column(Text, default="")
    body_zh: Mapped[str] = mapped_column(Text, default="")

    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tech: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    links: Mapped[dict] = mapped_column(JSONB, default=dict)
    period: Mapped[str | None] = mapped_column(String(80), nullable=True)
    role_en: Mapped[str | None] = mapped_column(String(160), nullable=True)
    role_zh: Mapped[str | None] = mapped_column(String(160), nullable=True)

    # SEO (nullable → frontend falls back to title / summary / cover_image)
    meta_title_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meta_title_zh: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meta_description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_description_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    og_image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    published: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    title_en: Mapped[str] = mapped_column(String(200))
    title_zh: Mapped[str] = mapped_column(String(200))
    excerpt_en: Mapped[str] = mapped_column(Text, default="")
    excerpt_zh: Mapped[str] = mapped_column(Text, default="")
    body_en: Mapped[str] = mapped_column(Text, default="")
    body_zh: Mapped[str] = mapped_column(Text, default="")

    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    reading_minutes: Mapped[int] = mapped_column(Integer, default=1)

    meta_title_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meta_title_zh: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meta_description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_description_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    og_image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    published: Mapped[bool] = mapped_column(Boolean, default=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
