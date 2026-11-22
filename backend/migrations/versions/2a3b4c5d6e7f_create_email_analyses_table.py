"""create email analyses table

Revision ID: 2a3b4c5d6e7f
Revises: 1f2e3d4c5b6a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2a3b4c5d6e7f"
down_revision: Union[str, Sequence[str], None] = "1f2e3d4c5b6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_analyses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email_id", sa.Integer(), nullable=False),
        sa.Column("suggested_category", sa.String(length=50), nullable=False),
        sa.Column("category_confidence", sa.Float(), nullable=False),
        sa.Column("category_explanation", sa.Text(), nullable=False),
        sa.Column("manual_category", sa.String(length=50), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("main_purpose", sa.Text(), nullable=False),
        sa.Column("important_points", sa.JSON(), nullable=False),
        sa.Column("required_action", sa.Text(), nullable=True),
        sa.Column("relevant_dates", sa.JSON(), nullable=False),
        sa.Column("extracted", sa.JSON(), nullable=False),
        sa.Column("security_risk", sa.String(length=20), nullable=False),
        sa.Column("security_warning_signs", sa.JSON(), nullable=False),
        sa.Column("security_explanation", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["email_id"], ["emails.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email_id"),
    )
    op.create_index("ix_email_analyses_id", "email_analyses", ["id"], unique=False)
    op.create_index("ix_email_analyses_user_id", "email_analyses", ["user_id"], unique=False)
    op.create_index("ix_email_analyses_email_id", "email_analyses", ["email_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_email_analyses_email_id", table_name="email_analyses")
    op.drop_index("ix_email_analyses_user_id", table_name="email_analyses")
    op.drop_index("ix_email_analyses_id", table_name="email_analyses")
    op.drop_table("email_analyses")
