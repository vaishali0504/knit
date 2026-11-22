from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for registering a new user."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=6, description="User password (min 6 chars)")
    full_name: Optional[str] = Field(default=None, description="Optional user full name")


class UserLogin(BaseModel):
    """Schema for logging in."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")


class UserResponse(BaseModel):
    """Schema for returning user data."""

    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
