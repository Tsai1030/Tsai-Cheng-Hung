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
    likes: int = 0
    views: int = 0


class ProjectDetail(ProjectCard):
    body_en: str
    body_zh: str
    video_url: str | None = None
    github_stars: int | None = None
    github_forks: int | None = None
    meta_title_en: str | None = None
    meta_title_zh: str | None = None
    meta_description_en: str | None = None
    meta_description_zh: str | None = None
    og_image: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------- Likes ----------
class LikeCount(BaseModel):
    likes: int


# ---------- Views ----------
class ViewCount(BaseModel):
    views: int


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
    likes: int = 0
    views: int = 0


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


class PostUpsert(BaseModel):
    """Payload for the admin write endpoint (POST /posts). Upserts by slug."""

    slug: str
    title_en: str
    title_zh: str
    excerpt_en: str = ""
    excerpt_zh: str = ""
    body_en: str = ""
    body_zh: str = ""
    cover_image: str | None = None
    tags: list[str] = []
    reading_minutes: int = 1
    published: bool = True
    published_at: datetime | None = None
    meta_title_en: str | None = None
    meta_title_zh: str | None = None
    meta_description_en: str | None = None
    meta_description_zh: str | None = None
    og_image: str | None = None
