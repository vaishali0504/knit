"""create in-app reply drafts

Revision ID: 5d6e7f8091a2
Revises: 4c5d6e7f8091
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5d6e7f8091a2"
down_revision: Union[str, Sequence[str], None] = "4c5d6e7f8091"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reply_drafts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email_id", sa.Integer(), nullable=False),
        sa.Column("tone", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["email_id"], ["emails.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "email_id", name="uq_reply_drafts_user_email"),
    )
    op.create_index("ix_reply_drafts_id", "reply_drafts", ["id"], unique=False)
    op.create_index("ix_reply_drafts_user_id", "reply_drafts", ["user_id"], unique=False)
    op.create_index("ix_reply_drafts_email_id", "reply_drafts", ["email_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reply_drafts_email_id", table_name="reply_drafts")
    op.drop_index("ix_reply_drafts_user_id", table_name="reply_drafts")
    op.drop_index("ix_reply_drafts_id", table_name="reply_drafts")
    op.drop_table("reply_drafts")
