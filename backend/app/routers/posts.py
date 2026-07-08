from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_session
from ..models import Post
from ..schemas import LikeCount, PostCard, PostDetail, PostUpsert, ViewCount

router = APIRouter(prefix="/posts", tags=["posts"])


def require_admin(authorization: str | None = Header(default=None)) -> None:
    """Guard for admin write endpoints. Expects `Authorization: Bearer <ADMIN_TOKEN>`."""
    settings = get_settings()
    if not settings.admin_token:
        raise HTTPException(status_code=503, detail="Admin writes are disabled")
    if authorization != f"Bearer {settings.admin_token}":
        raise HTTPException(status_code=401, detail="Invalid admin token")


@router.get("", response_model=list[PostCard])
async def list_posts(
    published: bool = True,
    tag: str | None = None,
    exclude_tag: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[Post]:
    stmt = select(Post)
    if published:
        stmt = stmt.where(Post.published.is_(True))
    if tag:
        stmt = stmt.where(Post.tags.any(tag))
    if exclude_tag:
        stmt = stmt.where(~Post.tags.any(exclude_tag))
    stmt = stmt.order_by(Post.published_at.desc().nullslast(), Post.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=PostDetail, dependencies=[Depends(require_admin)])
async def upsert_post(
    payload: PostUpsert, session: AsyncSession = Depends(get_session)
) -> Post:
    """Create or update (by slug) a blog post. Admin-only."""
    result = await session.execute(select(Post).where(Post.slug == payload.slug))
    post = result.scalar_one_or_none()

    data = payload.model_dump()
    if data.get("published") and data.get("published_at") is None:
        data["published_at"] = datetime.now(timezone.utc)

    if post is None:
        post = Post(**data)
        session.add(post)
    else:
        for key, value in data.items():
            setattr(post, key, value)

    await session.commit()
    await session.refresh(post)
    return post


@router.get("/{slug}", response_model=PostDetail)
async def get_post(slug: str, session: AsyncSession = Depends(get_session)) -> Post:
    result = await session.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/{post_id}/like", response_model=LikeCount)
async def like_post(
    post_id: int, session: AsyncSession = Depends(get_session)
) -> dict[str, int]:
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(likes=Post.likes + 1)
        .returning(Post.likes)
    )
    likes = (await session.execute(stmt)).scalar_one_or_none()
    if likes is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await session.commit()
    return {"likes": likes}


@router.post("/{post_id}/view", response_model=ViewCount)
async def view_post(
    post_id: int, session: AsyncSession = Depends(get_session)
) -> dict[str, int]:
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(views=Post.views + 1)
        .returning(Post.views)
    )
    views = (await session.execute(stmt)).scalar_one_or_none()
    if views is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await session.commit()
    return {"views": views}


@router.post("/{post_id}/unlike", response_model=LikeCount)
async def unlike_post(
    post_id: int, session: AsyncSession = Depends(get_session)
) -> dict[str, int]:
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(likes=func.greatest(Post.likes - 1, 0))
        .returning(Post.likes)
    )
    likes = (await session.execute(stmt)).scalar_one_or_none()
    if likes is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await session.commit()
    return {"likes": likes}
