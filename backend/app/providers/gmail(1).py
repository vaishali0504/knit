from typing import Any
from urllib.parse import quote

import httpx

from app.providers.email_provider import HistoryPage, ProviderPage


GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"


class GmailProviderError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _error_code(status_code: int) -> str:
    if status_code == 401:
        return "reauthorization_required"
    if status_code == 403:
        return "permission_denied"
    if status_code == 404:
        return "message_not_found"
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "provider_unavailable"
    return "provider_request_failed"


class GmailProvider:
    """Read-only Gmail REST API adapter. It never mutates Gmail data."""

    def __init__(self, access_token: str, timeout_seconds: float = 20):
        self._access_token = access_token
        self._timeout = timeout_seconds

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = httpx.get(
                f"{GMAIL_API_BASE}/{path}",
                params=params,
                headers={"Authorization": f"Bearer {self._access_token}", "Accept": "application/json"},
                timeout=self._timeout,
            )
            if response.status_code >= 400:
                raise GmailProviderError(_error_code(response.status_code))
            payload = response.json()
            if not isinstance(payload, dict):
                raise GmailProviderError("invalid_provider_response")
            return payload
        except GmailProviderError:
            raise
        except httpx.TimeoutException as exc:
            raise GmailProviderError("provider_timeout") from exc
        except httpx.HTTPError as exc:
            raise GmailProviderError("provider_unavailable") from exc
        except (ValueError, TypeError) as exc:
            raise GmailProviderError("invalid_provider_response") from exc

    def account_identity(self) -> str:
        profile = self._get("profile")
        address = profile.get("emailAddress")
        if not isinstance(address, str) or "@" not in address:
            raise GmailProviderError("invalid_account_identity")
        return address.strip().lower()

    def list_messages(self, page_token: str | None, page_size: int) -> ProviderPage:
        params: dict[str, Any] = {"maxResults": min(max(page_size, 1), 100)}
        if page_token:
            if len(page_token) > 4096:
                raise GmailProviderError("invalid_page_token")
            params["pageToken"] = page_token
        payload = self._get("messages", params)
        messages = payload.get("messages", [])
        if not isinstance(messages, list):
            raise GmailProviderError("invalid_provider_response")
        next_token = payload.get("nextPageToken")
        return ProviderPage(messages=[item for item in messages if isinstance(item, dict)], next_page_token=next_token if isinstance(next_token, str) else None)

    def get_message(self, message_id: str) -> dict[str, Any]:
        if not message_id or len(message_id) > 512:
            raise GmailProviderError("invalid_message_id")
        return self._get(f"messages/{quote(message_id, safe='')}", {"format": "full"})

    def current_history_id(self) -> str:
        profile = self._get("profile")
        history_id = profile.get("historyId")
        if not isinstance(history_id, str) or not history_id:
            raise GmailProviderError("invalid_provider_response")
        return history_id

    def list_history(self, start_history_id: str, page_token: str | None, page_size: int) -> HistoryPage:
        params: dict[str, Any] = {
            "startHistoryId": start_history_id,
            "maxResults": min(max(page_size, 1), 100),
            "historyTypes": ["messageAdded", "messageDeleted", "labelAdded", "labelRemoved"],
        }
        if page_token:
            if len(page_token) > 4096:
                raise GmailProviderError("invalid_page_token")
            params["pageToken"] = page_token
        try:
            payload = self._get("history", params)
        except GmailProviderError as exc:
            if exc.code == "message_not_found":
                raise GmailProviderError("history_cursor_invalid") from None
            raise
        history = payload.get("history", [])
        if not isinstance(history, list):
            raise GmailProviderError("invalid_provider_response")
        next_token = payload.get("nextPageToken")
        history_id = payload.get("historyId")
        return HistoryPage(
            history=[entry for entry in history if isinstance(entry, dict)],
            next_page_token=next_token if isinstance(next_token, str) else None,
            history_id=history_id if isinstance(history_id, str) else None,
        )
