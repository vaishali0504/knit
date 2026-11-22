from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


TaskPriority = Literal["low", "medium", "high"]
TaskStatus = Literal["pending", "in_progress", "completed"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    due_at: Optional[datetime] = None
    priority: TaskPriority = "medium"
    status: TaskStatus = "pending"
    source_email_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    due_at: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    source_email_id: Optional[int] = None


class SourceEmailResponse(BaseModel):
    id: int
    subject: str
    sender_name: str

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_at: Optional[datetime]
    priority: str
    status: str
    completed_at: Optional[datetime]
    source_email_id: Optional[int]
    source_email: Optional[SourceEmailResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TaskCounts(BaseModel):
    all: int
    pending: int
    in_progress: int
    completed: int
    upcoming: int
