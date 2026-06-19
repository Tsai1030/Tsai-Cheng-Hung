"""add likes to projects and posts

Revision ID: f1a2b3c4d5e6
Revises: a1c9f4d2b8e0
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'a1c9f4d2b8e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('likes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('posts', sa.Column('likes', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('posts', 'likes')
    op.drop_column('projects', 'likes')
