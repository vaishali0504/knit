from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Email(Base, TimestampMixin):
    """Locally stored demonstration email owned by a KNIT user."""

    __tablename__ = "emails"
    __table_args__ = (
        UniqueConstraint("connected_account_id", "provider_message_id", name="uq_emails_connected_provider_message"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_name = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    is_important = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    attachments = Column(JSON, nullable=False, default=list)
    connected_account_id = Column(Integer, ForeignKey("connected_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    provider_message_id = Column(String(255), nullable=True, index=True)
    provider_thread_id = Column(String(255), nullable=True, index=True)
    provider_sync_seen_at = Column(DateTime(timezone=True), nullable=True)
    is_read_user_modified = Column(Boolean, default=False, nullable=False)
    is_important_user_modified = Column(Boolean, default=False, nullable=False)
    is_deleted_user_modified = Column(Boolean, default=False, nullable=False)

    owner = relationship("User")
    connected_account = relationship("ConnectedAccount")

    def __repr__(self) -> str:
        return f"<Email(id={self.id})>"
