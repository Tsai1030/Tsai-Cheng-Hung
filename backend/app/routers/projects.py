from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Project
from ..schemas import ProjectCard, ProjectDetail

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectCard])
async def list_projects(
    published: bool = True, session: AsyncSession = Depends(get_session)
) -> list[Project]:
    stmt = select(Project)
    if published:
        stmt = stmt.where(Project.published.is_(True))
    stmt = stmt.order_by(Project.featured.desc(), Project.sort.asc(), Project.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/{slug}", response_model=ProjectDetail)
async def get_project(slug: str, session: AsyncSession = Depends(get_session)) -> Project:
    result = await session.execute(select(Project).where(Project.slug == slug))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
