from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from cryptography.fernet import Fernet

from app.api.connections import _settings_redirect
from app.core.config import settings
from app.models import ConnectedAccount, Email, OAuthState
from app.services import gmail_oauth
from app.services.token_encryption import decrypt_token, encrypt_token
from conftest import TestingSessionLocal


def register(client, email):
    result = client.post("/api/auth/register", json={"email": email, "password": "strongpassword123", "full_name": "Test"})
    assert result.status_code == 201
    return {"Authorization": f"Bearer {result.json()['access_token']}"}


def enable_gmail(monkeypatch):
    monkeypatch.setattr(settings, "GMAIL_INTEGRATION_ENABLED", True)
    monkeypatch.setattr(settings, "FRONTEND_URL", "")
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "client-id")
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "client-secret")
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", "http://127.0.0.1:8000/api/connections/gmail/callback")
    monkeypatch.setattr(settings, "GMAIL_OAUTH_SCOPES", [gmail_oauth.READONLY_SCOPE])
    monkeypatch.setattr(settings, "GMAIL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode("ascii"))


class FakeResponse:
    def __init__(self, data, status=200):
        self.data = data
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise httpx.HTTPStatusError("provider failure", request=httpx.Request("GET", "https://google.test"), response=httpx.Response(self.status))

    def json(self):
        return self.data


def begin(client, headers):
    response = client.post("/api/connections/gmail/authorize", headers=headers)
    assert response.status_code == 200
    parsed = parse_qs(urlparse(response.json()["authorization_url"]).query)
    return parsed["state"][0], parsed


def test_connection_status_reports_disabled_gmail_without_credentials(client, monkeypatch):
    monkeypatch.setattr(settings, "GMAIL_INTEGRATION_ENABLED", False)
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
    monkeypatch.setattr(settings, "GMAIL_TOKEN_ENCRYPTION_KEY", "")
    monkeypatch.setattr(settings, "GMAIL_SYNC_MAX_MESSAGES", 100)
    monkeypatch.setattr(settings, "GMAIL_SYNC_PAGE_SIZE", 25)
    assert client.get("/api/connections/status").status_code == 401
    headers = register(client, "gmail-status@knit.app")
    result = client.get("/api/connections/status", headers=headers)
    assert result.status_code == 200
    assert result.json() == {
        "enabled": False,
        "credentials_configured": False,
        "sync_max_messages": 100,
        "sync_page_size": 25,
    }


def test_authorize_requires_auth_and_builds_readonly_offline_url(client, monkeypatch):
    enable_gmail(monkeypatch)
    assert client.post("/api/connections/gmail/authorize").status_code == 401
    headers = register(client, "oauth-start@knit.app")
    state, query = begin(client, headers)
    assert query["scope"] == [gmail_oauth.READONLY_SCOPE]
    assert query["access_type"] == ["offline"]
    assert query["redirect_uri"] == [settings.GOOGLE_OAUTH_REDIRECT_URI]
    db = TestingSessionLocal()
    try:
        state_row = db.query(OAuthState).filter(OAuthState.state_hash == gmail_oauth._state_hash(state)).one()
        assert state_row.state_hash != state
        assert state_row.consumed_at is None
    finally:
        db.close()


def test_callback_redirect_prefers_configured_frontend_url(monkeypatch):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://app.example.test/")
    monkeypatch.setattr(settings, "CORS_ORIGINS", ["http://localhost:5173"])

    assert _settings_redirect("connected") == "https://app.example.test/app/settings?gmail=connected"


def test_state_expiry_replay_and_mismatch_are_rejected(client, monkeypatch):
    enable_gmail(monkeypatch)
    headers = register(client, "oauth-state@knit.app")
    state, _ = begin(client, headers)
    db = TestingSessionLocal()
    try:
        state_row = db.query(OAuthState).filter(OAuthState.state_hash == gmail_oauth._state_hash(state)).one()
        state_row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
        with pytest.raises(gmail_oauth.GmailOAuthError):
            gmail_oauth.consume_state(db, state)
        state_row = db.query(OAuthState).filter(OAuthState.state_hash == gmail_oauth._state_hash(state)).one()
        state_row.expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        state_row.consumed_at = None
        db.commit()
        assert gmail_oauth.consume_state(db, state) > 0
        with pytest.raises(gmail_oauth.GmailOAuthError):
            gmail_oauth.consume_state(db, state)
        with pytest.raises(gmail_oauth.GmailOAuthError):
            gmail_oauth.consume_state(db, "not-the-state")
    finally:
        db.close()


def test_authorization_start_prunes_expired_and_consumed_states(client, monkeypatch):
    enable_gmail(monkeypatch)
    headers = register(client, "oauth-state-cleanup@knit.app")
    expired_state, _ = begin(client, headers)
    db = TestingSessionLocal()
    try:
        row = db.query(OAuthState).filter_by(state_hash=gmail_oauth._state_hash(expired_state)).one()
        row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    finally:
        db.close()

    next_state, _ = begin(client, headers)
    db = TestingSessionLocal()
    try:
        assert db.query(OAuthState).filter_by(state_hash=gmail_oauth._state_hash(expired_state)).count() == 0
        assert db.query(OAuthState).filter_by(state_hash=gmail_oauth._state_hash(next_state)).count() == 1
    finally:
        db.close()


def test_callback_binds_user_encrypts_tokens_and_returns_safe_metadata(client, monkeypatch):
    enable_gmail(monkeypatch)
    headers = register(client, "oauth-callback@knit.app")
    other_headers = register(client, "oauth-callback-other@knit.app")
    state, _ = begin(client, headers)

    def fake_post(url, **kwargs):
        assert url == gmail_oauth.GOOGLE_TOKEN_URL
        assert kwargs["data"]["client_secret"] == "client-secret"
        return FakeResponse({"access_token": "access-secret", "refresh_token": "refresh-secret", "expires_in": 3600, "scope": gmail_oauth.READONLY_SCOPE})

    def fake_get(url, **kwargs):
        assert url == gmail_oauth.GMAIL_PROFILE_URL
        assert kwargs["headers"]["Authorization"] == "Bearer access-secret"
        return FakeResponse({"emailAddress": "person@gmail.test", "messagesTotal": 42})

    monkeypatch.setattr(gmail_oauth.httpx, "post", fake_post)
    monkeypatch.setattr(gmail_oauth.httpx, "get", fake_get)
    callback = client.get("/api/connections/gmail/callback", params={"state": state, "code": "test-code", "next": "https://attacker.test"}, follow_redirects=False)
    assert callback.status_code == 302
    assert callback.headers["location"] == "http://localhost:5173/app/settings?gmail=connected"
    assert callback.headers["Cache-Control"] == "no-store"
    assert callback.headers["Referrer-Policy"] == "no-referrer"
    assert "test-code" not in callback.text and "test-code" not in callback.headers["location"]

    listed = client.get("/api/connections", headers=headers)
    assert listed.status_code == 200
    payload = listed.json()
    serialized = str(payload)
    assert payload["items"][0]["email_address"] == "person@gmail.test"
    assert "access-secret" not in serialized and "refresh-secret" not in serialized
    assert "encrypted_" not in serialized and "provider_account_id" not in serialized
    assert client.get("/api/connections", headers=other_headers).json()["items"] == []
    db = TestingSessionLocal()
    try:
        owner_id = client.get("/api/auth/me", headers=headers).json()["id"]
        account = db.query(ConnectedAccount).filter_by(provider_account_id="person@gmail.test").one()
        assert account.user_id == owner_id
        assert account.encrypted_access_token != "access-secret"
        assert decrypt_token(account.encrypted_access_token) == "access-secret"
        assert decrypt_token(account.encrypted_refresh_token) == "refresh-secret"
    finally:
        db.close()


def test_existing_refresh_token_is_preserved_when_google_omits_it(client, monkeypatch):
    enable_gmail(monkeypatch)
    headers = register(client, "oauth-refresh@knit.app")
    state, _ = begin(client, headers)
    monkeypatch.setattr(gmail_oauth.httpx, "post", lambda url, **kwargs: FakeResponse({"access_token": "new-access", "expires_in": 1200, "scope": gmail_oauth.READONLY_SCOPE}))
    monkeypatch.setattr(gmail_oauth.httpx, "get", lambda url, **kwargs: FakeResponse({"emailAddress": "refresh@gmail.test"}))
    db = TestingSessionLocal()
    try:
        from app.models.user import User
        user_id = db.query(User).filter_by(email="oauth-refresh@knit.app").one().id
        db.add(ConnectedAccount(user_id=user_id, provider="gmail", provider_account_id="refresh@gmail.test", email_address="refresh@gmail.test", encrypted_access_token=encrypt_token("old-access"), encrypted_refresh_token=encrypt_token("keep-refresh"), granted_scopes=[gmail_oauth.READONLY_SCOPE], sync_status="pending"))
        db.commit()
    finally:
        db.close()
    client.get("/api/connections/gmail/callback", params={"state": state, "code": "second-code"}, follow_redirects=False)
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(provider_account_id="refresh@gmail.test").one()
        assert decrypt_token(account.encrypted_refresh_token) == "keep-refresh"
    finally:
        db.close()


def test_oauth_denial_and_provider_errors_redirect_safely(client, monkeypatch, caplog):
    enable_gmail(monkeypatch)
    headers = register(client, "oauth-errors@knit.app")
    denied_state, _ = begin(client, headers)
    denied = client.get("/api/connections/gmail/callback", params={"state": denied_state, "error": "access_denied", "next": "https://attacker.test"}, follow_redirects=False)
    assert denied.headers["location"] == "http://localhost:5173/app/settings?gmail=denied"
    failed_state, _ = begin(client, headers)
    monkeypatch.setattr(gmail_oauth.httpx, "post", lambda *args, **kwargs: (_ for _ in ()).throw(httpx.ConnectError("secret-containing provider text")))
    failed = client.get("/api/connections/gmail/callback", params={"state": failed_state, "code": "test-code"}, follow_redirects=False)
    assert failed.headers["location"] == "http://localhost:5173/app/settings?gmail=error"
    assert "secret-containing" not in failed.text
    assert "secret-containing" not in caplog.text


def test_callback_rejects_broader_granted_scope(client, monkeypatch):
    enable_gmail(monkeypatch)
    headers = register(client, "oauth-scope-reject@knit.app")
    state, _ = begin(client, headers)
    monkeypatch.setattr(gmail_oauth.httpx, "post", lambda *args, **kwargs: FakeResponse({
        "access_token": "mock-access",
        "refresh_token": "mock-refresh",
        "expires_in": 3600,
        "scope": f"{gmail_oauth.READONLY_SCOPE} https://www.googleapis.com/auth/gmail.modify",
    }))
    monkeypatch.setattr(gmail_oauth.httpx, "get", lambda *args, **kwargs: pytest.fail("profile should not be requested for broader scopes"))

    response = client.get("/api/connections/gmail/callback", params={"state": state, "code": "mock-code"}, follow_redirects=False)
    assert response.headers["location"] == "http://localhost:5173/app/settings?gmail=error"
    assert client.get("/api/connections", headers=headers).json()["items"] == []


def test_disconnect_is_user_scoped_and_keeps_email(client, monkeypatch):
    enable_gmail(monkeypatch)
    owner_headers = register(client, "oauth-owner@knit.app")
    other_headers = register(client, "oauth-other@knit.app")
    state, _ = begin(client, owner_headers)
    monkeypatch.setattr(gmail_oauth.httpx, "post", lambda *args, **kwargs: FakeResponse({"access_token": "a", "refresh_token": "r", "expires_in": 3600, "scope": gmail_oauth.READONLY_SCOPE}))
    monkeypatch.setattr(gmail_oauth.httpx, "get", lambda *args, **kwargs: FakeResponse({"emailAddress": "disconnect@gmail.test"}))
    client.get("/api/connections/gmail/callback", params={"state": state, "code": "c"}, follow_redirects=False)
    listing = client.get("/api/connections", headers=owner_headers).json()["items"]
    account_id = listing[0]["id"]
    db = TestingSessionLocal()
    try:
        owner = db.query(ConnectedAccount).filter_by(id=account_id).one()
        linked_email = Email(
            user_id=owner.user_id,
            connected_account_id=owner.id,
            provider_message_id="preserve-on-disconnect",
            provider_thread_id="preserve-thread",
            sender_name="Sender",
            sender_email="sender@example.test",
            recipient=owner.email_address,
            subject="Keep this KNIT record",
            body="Example content",
            received_at=datetime.now(timezone.utc),
            category="other",
        )
        db.add(linked_email)
        db.commit()
        linked_email_id = linked_email.id
    finally:
        db.close()
    assert client.delete(f"/api/connections/{account_id}", headers=other_headers).status_code == 404
    monkeypatch.setattr(gmail_oauth.httpx, "post", lambda *args, **kwargs: (_ for _ in ()).throw(httpx.ConnectError("refresh-secret leak canary")))
    deleted = client.delete(f"/api/connections/{account_id}", headers=owner_headers)
    assert deleted.status_code == 204
    assert client.get("/api/connections", headers=owner_headers).json()["items"] == []
    db = TestingSessionLocal()
    try:
        preserved = db.query(Email).filter_by(id=linked_email_id).one()
        assert preserved.connected_account_id is None
        assert preserved.subject == "Keep this KNIT record"
    finally:
        db.close()

