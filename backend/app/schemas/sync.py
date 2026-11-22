from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SyncResponse(BaseModel):
    sync_type: Literal["initial", "incremental"]
    status: str
    added: int
    updated: int
    removed: int
    last_successful_sync_at: datetime | None
    imported: int
    skipped: int
    failed: int
    limit_reached: bool
    error_code: str | None = None
    message: str | None = None
