"""add Gmail sync lease timestamp

Revision ID: 8a9b0c1d2e3f
Revises: 7f8091a2b3c4
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8a9b0c1d2e3f"
down_revision: Union[str, Sequence[str], None] = "7f8091a2b3c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("connected_accounts", sa.Column("sync_started_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("connected_accounts", "sync_started_at")
