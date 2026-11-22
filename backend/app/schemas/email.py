from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AttachmentResponse(BaseModel):
    name: str
    filename: str
    size: str
    is_demo: bool = True

    model_config = ConfigDict(from_attributes=True)


class EmailResponse(BaseModel):
    id: int
    sender_name: str
    sender_email: str
    recipient: str
    subject: str
    body: str
    received_at: datetime
    category: str
    is_read: bool
    is_important: bool
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    attachments: List[AttachmentResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class EmailListItem(BaseModel):
    id: int
    sender_name: str
    sender_email: str
    subject: str
    preview: str
    received_at: datetime
    category: str
    is_read: bool
    is_important: bool
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    attachment_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class EmailListResponse(BaseModel):
    items: List[EmailListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class EmailActionResponse(BaseModel):
    id: int
    is_read: bool
    is_important: bool
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EmailCounts(BaseModel):
    all: int
    internship: int
    interview: int
    college: int
    important: int
    personal: int
    promotions: int
    updates: int
    suspicious: int
    other: int
    unread: int
    deleted: int
