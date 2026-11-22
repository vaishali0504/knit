from sqlalchemy import Boolean, Column, Integer, String
from app.core.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """User account model for KNIT platform."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
