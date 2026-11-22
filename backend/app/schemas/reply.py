from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReplyTone = Literal["professional", "friendly", "formal", "short_direct"]


class ReplyGenerationRequest(BaseModel):
    tone: ReplyTone

    model_config = ConfigDict(extra="forbid")


class ReplyProviderOutput(BaseModel):
    reply_body: str = Field(min_length=1, max_length=12000)

    model_config = ConfigDict(str_strip_whitespace=True)


class ReplyGenerationResponse(BaseModel):
    email_id: int
    tone: ReplyTone
    reply_body: str = Field(min_length=1, max_length=12000)

    model_config = ConfigDict(str_strip_whitespace=True)


class ReplyDraftUpdate(BaseModel):
    tone: ReplyTone
    content: str = Field(min_length=1, max_length=12000)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class ReplyDraftResponse(BaseModel):
    id: int
    email_id: int
    tone: ReplyTone
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
