"""add views to projects and posts

Per-item page-view counter, mirroring `likes`. Incremented once per visitor
session from the detail page (see frontend ViewPing); displayed on the cards.

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2
Create Date: 2026-06-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8d9e0f1a2b3'
down_revision: Union[str, None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('views', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('posts', sa.Column('views', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('posts', 'views')
    op.drop_column('projects', 'views')
