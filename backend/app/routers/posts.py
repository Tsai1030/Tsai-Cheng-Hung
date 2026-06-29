from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Post
from ..schemas import LikeCount, PostCard, PostDetail, ViewCount

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
