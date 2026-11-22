"""add per-run synchronization lease ownership token

Revision ID: a10c3d4e5f67
Revises: 9b0c1d2e3f4a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a10c3d4e5f67"
down_revision: Union[str, Sequence[str], None] = "9b0c1d2e3f4a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("connected_accounts", sa.Column("sync_lease_token", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("connected_accounts", "sync_lease_token")
