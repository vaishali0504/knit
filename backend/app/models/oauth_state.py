from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index

from app.core.database import Base
from app.models.base import TimestampMixin


class OAuthState(Base, TimestampMixin):
    __tablename__ = "oauth_states"
    __table_args__ = (Index("ix_oauth_states_expires_at", "expires_at"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    state_hash = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
