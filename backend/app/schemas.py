from datetime import datetime

from pydantic import BaseModel, ConfigDict


class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Projects ----------
class ProjectCard(_ORM):
    id: int
    slug: str
    title_en: str
    title_zh: str
    summary_en: str
    summary_zh: str
    cover_image: str | None = None
    tech: list[str] = []
    links: dict = {}
    period: str | None = None
    role_en: str | None = None
    role_zh: str | None = None
    featured: bool = False


class ProjectDetail(ProjectCard):
    body_en: str
    body_zh: str
    meta_title_en: str | None = None
    meta_title_zh: str | None = None
    meta_description_en: str | None = None
    meta_description_zh: str | None = None
    og_image: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------- Posts ----------
class PostCard(_ORM):
    id: int
    slug: str
    title_en: str
    title_zh: str
    excerpt_en: str
    excerpt_zh: str
    cover_image: str | None = None
    tags: list[str] = []
    reading_minutes: int = 1
    published_at: datetime | None = None


class PostDetail(PostCard):
    body_en: str
    body_zh: str
    meta_title_en: str | None = None
    meta_title_zh: str | None = None
    meta_description_en: str | None = None
    meta_description_zh: str | None = None
    og_image: str | None = None
    created_at: datetime
    updated_at: datetime
