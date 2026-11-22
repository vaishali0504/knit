from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class EmailAnalysis(Base, TimestampMixin):
    __tablename__ = "email_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    suggested_category = Column(String(50), nullable=False)
    category_confidence = Column(Float, nullable=False)
    category_explanation = Column(Text, nullable=False)
    manual_category = Column(String(50), nullable=True)
    summary = Column(Text, nullable=False)
    main_purpose = Column(Text, nullable=False)
    important_points = Column(JSON, nullable=False, default=list)
    required_action = Column(Text, nullable=True)
    relevant_dates = Column(JSON, nullable=False, default=list)
    extracted = Column(JSON, nullable=False, default=dict)
    security_risk = Column(String(20), nullable=False)
    security_warning_signs = Column(JSON, nullable=False, default=list)
    security_explanation = Column(Text, nullable=False)
    model_name = Column(String(100), nullable=False)
    prompt_version = Column(String(20), nullable=False, default="p5-v1")

    owner = relationship("User")
    email = relationship("Email")
