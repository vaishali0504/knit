from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class ReplyDraft(Base, TimestampMixin):
    __tablename__ = "reply_drafts"
    __table_args__ = (
        UniqueConstraint("user_id", "email_id", name="uq_reply_drafts_user_email"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    tone = Column(String(30), nullable=False)
    content = Column(Text, nullable=False)

    owner = relationship("User")
    email = relationship("Email")
