from typing import Any

from app.core.config import settings


class OAuthCallbackQueryRedactionMiddleware:
    """Remove OAuth callback query parameters before server access logging."""

    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        callback_path = f"{settings.API_V1_PREFIX.rstrip('/')}/connections/gmail/callback"
        if scope.get("type") != "http" or scope.get("path") != callback_path:
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        finally:
            # Uvicorn formats its access-log request line after the ASGI app
            # returns, using the same mutable scope and its query_string.
            scope["query_string"] = b""
