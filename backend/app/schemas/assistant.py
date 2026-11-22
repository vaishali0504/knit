from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AssistantConversationCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)


class AssistantMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class AssistantReferenceResponse(BaseModel):
    email_id: int
    subject: str
    sender_name: str
    sender_email: str


class AssistantMessageResponse(BaseModel):
    id: int
    role: Literal["user", "assistant", "system"]
    content: str
    references: list[AssistantReferenceResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssistantConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[AssistantMessageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AssistantConversationListItem(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class AssistantConversationListResponse(BaseModel):
    items: list[AssistantConversationListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AssistantProviderOutput(BaseModel):
    answer: str = Field(min_length=1, max_length=5000)
    source_email_ids: list[int] = Field(default_factory=list, max_length=8)
