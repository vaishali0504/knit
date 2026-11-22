import asyncio
import logging

from app.middleware import OAuthCallbackQueryRedactionMiddleware
from app.models.email import Email
from uvicorn.protocols.utils import get_path_with_query_string


def test_oauth_callback_query_is_available_to_app_but_redacted_from_captured_access_log(caplog):
    observed_by_route = []
    scope = {
        "type": "http",
        "path": "/api/connections/gmail/callback",
        "query_string": b"state=state-canary&code=code-canary",
    }

    async def app(inner_scope, receive, send):
        observed_by_route.append(inner_scope["query_string"])

    access_logger = logging.getLogger("uvicorn.access")
    with caplog.at_level(logging.INFO, logger="uvicorn.access"):
        asyncio.run(OAuthCallbackQueryRedactionMiddleware(app)(scope, None, None))
        access_logger.info('test-client - "GET %s HTTP/1.1" 302', get_path_with_query_string(scope))

    assert observed_by_route == [b"state=state-canary&code=code-canary"]
    assert "state-canary" not in caplog.text
    assert "code-canary" not in caplog.text
    assert "/api/connections/gmail/callback" in caplog.text


def test_email_model_repr_does_not_include_user_content():
    email = Email(id=1, subject="private subject canary")
    assert "private subject canary" not in repr(email)
    assert "id=1" in repr(email)
