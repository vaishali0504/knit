"""add Gmail history and resync state

Revision ID: 9b0c1d2e3f4a
Revises: 8a9b0c1d2e3f
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "9b0c1d2e3f4a"
down_revision: Union[str, Sequence[str], None] = "8a9b0c1d2e3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("connected_accounts", sa.Column("gmail_sync_page_token", sa.Text(), nullable=True))
    op.add_column("connected_accounts", sa.Column("gmail_sync_baseline_history_id", sa.String(length=255), nullable=True))
    op.add_column("connected_accounts", sa.Column("full_resync_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("emails", sa.Column("provider_sync_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("emails", sa.Column("is_read_user_modified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("emails", sa.Column("is_important_user_modified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("emails", sa.Column("is_deleted_user_modified", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("emails", "is_deleted_user_modified")
    op.drop_column("emails", "is_important_user_modified")
    op.drop_column("emails", "is_read_user_modified")
    op.drop_column("emails", "provider_sync_seen_at")
    op.drop_column("connected_accounts", "full_resync_started_at")
    op.drop_column("connected_accounts", "gmail_sync_baseline_history_id")
    op.drop_column("connected_accounts", "gmail_sync_page_token")
