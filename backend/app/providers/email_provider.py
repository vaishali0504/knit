from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ProviderPage:
    messages: list[dict[str, Any]]
    next_page_token: str | None


@dataclass(frozen=True)
class HistoryPage:
    history: list[dict[str, Any]]
    next_page_token: str | None
    history_id: str | None


class EmailProvider(Protocol):
    """Small provider boundary required by initial email import."""

    def account_identity(self) -> str: ...

    def list_messages(self, page_token: str | None, page_size: int) -> ProviderPage: ...

    def get_message(self, message_id: str) -> dict[str, Any]: ...

    def current_history_id(self) -> str: ...

    def list_history(self, start_history_id: str, page_token: str | None, page_size: int) -> HistoryPage: ...
