from datetime import datetime, timezone
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for health check endpoint response."""

    status: str = Field(default="ok", description="Health status indicator")
    app_name: str = Field(description="Name of the application")
    version: str = Field(description="Application version")
    environment: str = Field(description="Current deployment environment")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current server timestamp (UTC)",
    )
