"""add connected accounts and provider email references

Revision ID: 6e7f8091a2b3
Revises: 5d6e7f8091a2
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6e7f8091a2b3"
down_revision: Union[str, Sequence[str], None] = "5d6e7f8091a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "connected_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_account_id", sa.String(length=255), nullable=False),
        sa.Column("email_address", sa.String(length=320), nullable=False),
        sa.Column("encrypted_access_token", sa.Text(), nullable=False),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=False),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("granted_scopes", sa.JSON(), nullable=False),
        sa.Column("gmail_history_id", sa.String(length=255), nullable=True),
        sa.Column("sync_status", sa.String(length=32), nullable=False),
        sa.Column("last_successful_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_error_code", sa.String(length=80), nullable=True),
        sa.Column("sync_error_message", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("provider = 'gmail'", name="ck_connected_accounts_supported_provider"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "provider", "provider_account_id", name="uq_connected_account_user_provider_account"),
    )
    op.create_index("ix_connected_accounts_user_id", "connected_accounts", ["user_id"])
    op.create_index("ix_connected_accounts_user_provider", "connected_accounts", ["user_id", "provider"])

    with op.batch_alter_table("emails") as batch_op:
        batch_op.add_column(sa.Column("connected_account_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("provider_message_id", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("provider_thread_id", sa.String(length=255), nullable=True))
        batch_op.create_foreign_key(
            "fk_emails_connected_account_id_connected_accounts",
            "connected_accounts",
            ["connected_account_id"], ["id"], ondelete="SET NULL",
        )
        batch_op.create_unique_constraint(
            "uq_emails_connected_provider_message", ["connected_account_id", "provider_message_id"]
        )
    op.create_index("ix_emails_connected_account_id", "emails", ["connected_account_id"])
    op.create_index("ix_emails_provider_message_id", "emails", ["provider_message_id"])
    op.create_index("ix_emails_provider_thread_id", "emails", ["provider_thread_id"])


def downgrade() -> None:
    op.drop_index("ix_emails_provider_thread_id", table_name="emails")
    op.drop_index("ix_emails_provider_message_id", table_name="emails")
    op.drop_index("ix_emails_connected_account_id", table_name="emails")
    with op.batch_alter_table("emails") as batch_op:
        batch_op.drop_constraint("uq_emails_connected_provider_message", type_="unique")
        batch_op.drop_constraint("fk_emails_connected_account_id_connected_accounts", type_="foreignkey")
        batch_op.drop_column("provider_thread_id")
        batch_op.drop_column("provider_message_id")
        batch_op.drop_column("connected_account_id")
    op.drop_index("ix_connected_accounts_user_provider", table_name="connected_accounts")
    op.drop_index("ix_connected_accounts_user_id", table_name="connected_accounts")
    op.drop_table("connected_accounts")
