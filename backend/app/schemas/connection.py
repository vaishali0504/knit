from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GmailAuthorizeResponse(BaseModel):
    authorization_url: str


class ConnectedAccountResponse(BaseModel):
    id: int
    provider: Literal["gmail"]
    email_address: str
    status: str
    scopes: list[str]
    last_successful_sync_at: datetime | None


class ConnectedAccountsResponse(BaseModel):
    items: list[ConnectedAccountResponse]


class GmailSyncSettingsUpdate(BaseModel):
    sync_max_messages: int = Field(default=100, ge=1, le=500)
    sync_page_size: int = Field(default=25, ge=1, le=100)
