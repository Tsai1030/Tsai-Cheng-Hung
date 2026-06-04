"""SQLAlchemy models.

Real tables (projects, posts) are added in Stage 1; doc_chunks in Stage 5.
Importing this module registers all model metadata on Base so Alembic
autogenerate can see them.
"""

from .db import Base  # noqa: F401

# Stage 1 will define here:
#   class Project(Base): __tablename__ = "projects" ...
#   class Post(Base):    __tablename__ = "posts" ...
