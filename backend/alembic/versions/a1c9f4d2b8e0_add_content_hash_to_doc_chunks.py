"""add content_hash to doc_chunks

Revision ID: a1c9f4d2b8e0
Revises: 7e905c48a5ce
Create Date: 2026-06-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c9f4d2b8e0'
down_revision: Union[str, None] = '7e905c48a5ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Nullable: existing rows have no hash, so the first sync treats every
    # source as changed and rebuilds it once.
    op.add_column('doc_chunks', sa.Column('content_hash', sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column('doc_chunks', 'content_hash')
