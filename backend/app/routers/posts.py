from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Post
from ..schemas import PostCard, PostDetail

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostCard])
async def list_posts(
    published: bool = True, session: AsyncSession = Depends(get_session)
) -> list[Post]:
    stmt = select(Post)
    if published:
        stmt = stmt.where(Post.published.is_(True))
    stmt = stmt.order_by(Post.published_at.desc().nullslast(), Post.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/{slug}", response_model=PostDetail)
async def get_post(slug: str, session: AsyncSession = Depends(get_session)) -> Post:
    result = await session.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
