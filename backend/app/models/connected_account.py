from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint

from app.core.database import Base
from app.models.base import TimestampMixin


class ConnectedAccount(Base, TimestampMixin):
    """Provider account authorization and synchronization metadata."""

    __tablename__ = "connected_accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "provider_account_id", name="uq_connected_account_user_provider_account"),
        CheckConstraint("provider = 'gmail'", name="ck_connected_accounts_supported_provider"),
        Index("ix_connected_accounts_user_provider", "user_id", "provider"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(32), nullable=False, default="gmail")
    provider_account_id = Column(String(255), nullable=False)
    email_address = Column(String(320), nullable=False)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    granted_scopes = Column(JSON, nullable=False, default=list)
    gmail_history_id = Column(String(255), nullable=True)
    sync_status = Column(String(32), nullable=False, default="pending")
    sync_started_at = Column(DateTime(timezone=True), nullable=True)
    sync_lease_token = Column(String(64), nullable=True)
    gmail_sync_page_token = Column(Text, nullable=True)
    gmail_sync_baseline_history_id = Column(String(255), nullable=True)
    full_resync_started_at = Column(DateTime(timezone=True), nullable=True)
    last_successful_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_error_code = Column(String(80), nullable=True)
    sync_error_message = Column(String(500), nullable=True)

