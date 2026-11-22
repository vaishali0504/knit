"""create assistant conversation tables

Revision ID: 4c5d6e7f8091
Revises: 3b4c5d6e7f80
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4c5d6e7f8091"
down_revision: Union[str, Sequence[str], None] = "3b4c5d6e7f80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_conversations_id", "ai_conversations", ["id"], unique=False)
    op.create_index("ix_ai_conversations_user_id", "ai_conversations", ["user_id"], unique=False)

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_messages_id", "ai_messages", ["id"], unique=False)
    op.create_index("ix_ai_messages_conversation_id", "ai_messages", ["conversation_id"], unique=False)
    op.create_index("ix_ai_messages_user_id", "ai_messages", ["user_id"], unique=False)

    op.create_table(
        "ai_message_references",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("email_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["email_id"], ["emails.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["message_id"], ["ai_messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_message_references_id", "ai_message_references", ["id"], unique=False)
    op.create_index("ix_ai_message_references_message_id", "ai_message_references", ["message_id"], unique=False)
    op.create_index("ix_ai_message_references_email_id", "ai_message_references", ["email_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_message_references_email_id", table_name="ai_message_references")
    op.drop_index("ix_ai_message_references_message_id", table_name="ai_message_references")
    op.drop_index("ix_ai_message_references_id", table_name="ai_message_references")
    op.drop_table("ai_message_references")
    op.drop_index("ix_ai_messages_user_id", table_name="ai_messages")
    op.drop_index("ix_ai_messages_conversation_id", table_name="ai_messages")
    op.drop_index("ix_ai_messages_id", table_name="ai_messages")
    op.drop_table("ai_messages")
    op.drop_index("ix_ai_conversations_user_id", table_name="ai_conversations")
    op.drop_index("ix_ai_conversations_id", table_name="ai_conversations")
    op.drop_table("ai_conversations")
