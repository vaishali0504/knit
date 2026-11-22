from datetime import datetime, timedelta, timezone
import base64
import pytest

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.connected_account import ConnectedAccount
from app.models.email import Email
from app.models.user import User
from app.providers import gmail as gmail_provider
from app.services import email_sync
from app.services.email_sync import SyncError, _claim_sync, _finish, _heartbeat_sync
from app.services.token_encryption import decrypt_token, encrypt_token
from conftest import TestingSessionLocal


SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


def register(client: TestClient, email: str) -> tuple[dict[str, str], int]:
    response = client.post("/api/auth/register", json={"email": email, "password": "strongpassword123", "full_name": "Sync User"})
    assert response.status_code == 201
    token = response.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    return {"Authorization": f"Bearer {token}"}, me["id"]


def configure(monkeypatch, max_messages=100, page_size=25):
    monkeypatch.setattr(settings, "GMAIL_INTEGRATION_ENABLED", True)
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "test-client")
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setattr(settings, "GMAIL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode("ascii"))
    monkeypatch.setattr(settings, "GMAIL_SYNC_MAX_MESSAGES", max_messages)
    monkeypatch.setattr(settings, "GMAIL_SYNC_PAGE_SIZE", page_size)


def add_account(user_id: int, expiry=None) -> int:
    db = TestingSessionLocal()
    try:
        row = ConnectedAccount(
            user_id=user_id,
            provider="gmail",
            provider_account_id="owner@gmail.test",
            email_address="owner@gmail.test",
            encrypted_access_token=encrypt_token("old-access"),
            encrypted_refresh_token=encrypt_token("refresh-secret"),
            token_expires_at=expiry or datetime.now(timezone.utc) + timedelta(hours=1),
            granted_scopes=[SCOPE],
            sync_status="pending",
        )
        db.add(row)
        db.commit()
        return row.id
    finally:
        db.close()


class Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status_code = status

    def json(self):
        return self.payload


def gmail_message(message_id: str, subject="Hello", labels=None):
    enc = lambda text: base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")
    return {
        "id": message_id,
        "threadId": f"thread-{message_id}",
        "internalDate": "1790000000000",
        "labelIds": labels or ["INBOX", "UNREAD"],
        "snippet": "Fallback preview",
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": "Alice Example <alice@example.test>"},
                {"name": "To", "value": "Owner <owner@gmail.test>"},
                {"name": "Subject", "value": subject},
            ],
            "body": {"data": enc("Please review this untrusted email body.")},
            "parts": [{"filename": "notes.txt", "mimeType": "text/plain", "body": {"size": 12, "attachmentId": "attachment-id"}}],
        },
    }


def test_sync_paginates_normalizes_deduplicates_and_preserves_sample_emails(client, monkeypatch):
    configure(monkeypatch, max_messages=3, page_size=2)
    headers, user_id = register(client, "sync-pages@knit.app")
    account_id = add_account(user_id)
    calls = {"pages": [], "details": []}

    def fake_get(url, params=None, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "100"})
        if url.endswith("/history"):
            return Response({"history": [], "historyId": "100"})
        if url.endswith("/messages"):
            calls["pages"].append(params)
            if params.get("pageToken") == "next":
                return Response({"messages": [{"id": "m3"}]})
            return Response({"messages": [{"id": "m1"}, {"id": "m2"}], "nextPageToken": "next"})
        message_id = url.rsplit("/", 1)[-1]
        calls["details"].append(message_id)
        return Response(gmail_message(message_id, labels=["INBOX", "UNREAD", "IMPORTANT"]))

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    first = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert first.status_code == 200
    assert first.json() == {"sync_type": "initial", "status": "complete", "added": 3, "updated": 0, "removed": 0, "last_successful_sync_at": first.json()["last_successful_sync_at"], "imported": 3, "skipped": 0, "failed": 0, "limit_reached": False, "error_code": None, "message": None}
    second = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert second.json()["sync_type"] == "incremental"
    assert second.json()["imported"] == 0 and second.json()["added"] == 0
    assert "old-access" not in second.text and "refresh-secret" not in second.text
    assert len(calls["details"]) == 3

    db = TestingSessionLocal()
    try:
        imported = db.query(Email).filter_by(connected_account_id=account_id).all()
        samples = db.query(Email).filter(Email.user_id == user_id, Email.connected_account_id.is_(None)).count()
        assert len(imported) == 3
        assert samples == 0
        assert imported[0].provider_thread_id == "thread-m1"
        assert imported[0].is_read is False and imported[0].is_important is True
        assert imported[0].body == "Please review this untrusted email body."
        assert imported[0].attachments[0]["filename"] == "notes.txt"
        assert imported[0].attachments[0]["provider_attachment_id"] == "attachment-id"
        connection = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert connection.gmail_history_id == "100"
    finally:
        db.close()


def test_sync_is_user_scoped_and_requires_auth(client, monkeypatch):
    configure(monkeypatch)
    owner_headers, owner_id = register(client, "sync-owner@knit.app")
    other_headers, _ = register(client, "sync-other@knit.app")
    account_id = add_account(owner_id)
    assert client.post(f"/api/connections/{account_id}/sync").status_code == 401
    assert client.post(f"/api/connections/{account_id}/sync", headers=other_headers).status_code == 404
    assert client.post(f"/api/connections/{account_id}/sync", headers=owner_headers).status_code == 200


def test_expired_access_token_refreshes_and_rotates_tokens_encrypted(client, monkeypatch):
    configure(monkeypatch)
    headers, user_id = register(client, "sync-refresh@knit.app")
    account_id = add_account(user_id, datetime.now(timezone.utc) - timedelta(seconds=10))
    refresh_calls = []

    def fake_post(url, data, **kwargs):
        refresh_calls.append(data)
        return Response({"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 3600})

    def fake_get(url, params=None, headers=None, **kwargs):
        assert headers["Authorization"] == "Bearer new-access"
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "100"})
        return Response({"messages": []})

    monkeypatch.setattr(email_sync.httpx, "post", fake_post)
    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    response = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert response.json()["status"] == "complete"
    assert refresh_calls[0]["grant_type"] == "refresh_token"
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert decrypt_token(account.encrypted_access_token) == "new-access"
        assert decrypt_token(account.encrypted_refresh_token) == "new-refresh"
        assert account.encrypted_access_token != "new-access"
        assert account.last_successful_sync_at is not None
    finally:
        db.close()


def test_initial_sync_respects_configured_message_cap(client, monkeypatch):
    configure(monkeypatch, max_messages=1, page_size=1)
    headers, user_id = register(client, "sync-limit@knit.app")
    account_id = add_account(user_id)

    def fake_get(url, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "100"})
        if url.endswith("/messages"):
            return Response({"messages": [{"id": "m1"}], "nextPageToken": "more"})
        return Response(gmail_message("m1"))

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    response = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert response.json()["imported"] == 1
    assert response.json()["limit_reached"] is True


def test_revoked_credentials_and_rate_limits_are_sanitized(client, monkeypatch):
    configure(monkeypatch)
    headers, user_id = register(client, "sync-failures@knit.app")
    account_id = add_account(user_id, datetime.now(timezone.utc) - timedelta(minutes=5))
    monkeypatch.setattr(email_sync.httpx, "post", lambda *args, **kwargs: Response({"error": "invalid_grant", "error_description": "private provider details"}, 400))
    revoked = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert revoked.json()["error_code"] == "reauthorization_required"
    assert "private provider details" not in revoked.text

    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        account.sync_status = "pending"
        account.sync_started_at = None
        db.commit()
    finally:
        db.close()
    monkeypatch.setattr(email_sync.httpx, "post", lambda *args, **kwargs: Response({"error": "rate"}, 429))
    rate_limited = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert rate_limited.json()["error_code"] == "rate_limited"


def test_partial_sync_and_concurrent_sync_protection(client, monkeypatch):
    configure(monkeypatch)
    headers, user_id = register(client, "sync-partial@knit.app")
    account_id = add_account(user_id)
    call_count = 0

    def fake_get(url, params=None, **kwargs):
        nonlocal call_count
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "100"})
        if url.endswith("/messages"):
            return Response({"messages": [{"id": "good"}, {"id": "broken"}]})
        if url.endswith("/good"):
            return Response(gmail_message("good"))
        call_count += 1
        return Response({}, 503)

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    partial = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert partial.json()["status"] == "partial"
    assert partial.json()["imported"] == 1 and partial.json()["failed"] == 1

    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        account.sync_status = "syncing"
        account.sync_started_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()
    blocked = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert blocked.status_code == 409
    assert call_count == 1


def test_sync_lease_heartbeat_renews_only_the_current_live_lease(client, monkeypatch):
    configure(monkeypatch)
    _, user_id = register(client, "sync-lease-heartbeat@knit.app")
    account_id = add_account(user_id)
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        first_token = _claim_sync(db, account)
        assert first_token is not None
        assert _claim_sync(db, account) is None
        db.refresh(account)
        renewed_at = account.sync_started_at.replace(tzinfo=timezone.utc) if account.sync_started_at.tzinfo is None else account.sync_started_at
        assert renewed_at > datetime.now(timezone.utc) - timedelta(seconds=2)

        account.sync_started_at = datetime.now(timezone.utc) - timedelta(minutes=16)
        db.commit()
        with pytest.raises(SyncError) as error:
            _heartbeat_sync(db, account, first_token)
        assert error.value.code == "sync_lease_lost"

        replacement_token = _claim_sync(db, account)
        assert replacement_token is not None and replacement_token != first_token
        with pytest.raises(SyncError):
            _heartbeat_sync(db, account, first_token)
        assert _finish(db, account, first_token, "error") is False
        db.refresh(account)
        assert account.sync_status == "syncing"
        assert account.sync_lease_token == replacement_token
        _heartbeat_sync(db, account, replacement_token)
    finally:
        db.close()


def test_sync_worker_stops_when_lease_is_reclaimed(client, monkeypatch):
    configure(monkeypatch)
    headers, user_id = register(client, "sync-lease-lost@knit.app")
    account_id = add_account(user_id)
    replaced = False

    def fake_get(url, **kwargs):
        nonlocal replaced
        if url.endswith("/profile"):
            if not replaced:
                other_db = TestingSessionLocal()
                try:
                    other_db.query(ConnectedAccount).filter_by(id=account_id).update({
                        ConnectedAccount.sync_lease_token: "other-worker-lease",
                        ConnectedAccount.sync_started_at: datetime.now(timezone.utc),
                    })
                    other_db.commit()
                    replaced = True
                finally:
                    other_db.close()
            return Response({"emailAddress": "owner@gmail.test", "historyId": "500"})
        raise AssertionError("the stale worker must stop before message listing")

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    response = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert response.status_code == 409
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert account.sync_status == "syncing"
        assert account.sync_lease_token == "other-worker-lease"
        assert account.gmail_history_id is None
    finally:
        db.close()


def test_incremental_history_paginates_and_duplicate_events_are_idempotent(client, monkeypatch):
    configure(monkeypatch, max_messages=20, page_size=10)
    headers, user_id = register(client, "sync-history-pages@knit.app")
    account_id = add_account(user_id)
    db = TestingSessionLocal()
    try:
        db.query(ConnectedAccount).filter_by(id=account_id).update({ConnectedAccount.gmail_history_id: "100"})
        db.commit()
    finally:
        db.close()
    history_calls = []

    def fake_get(url, params=None, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "105"})
        if url.endswith("/history"):
            history_calls.append(params)
            if params.get("pageToken") == "h2":
                return Response({"history": [{"id": "104", "messagesAdded": [{"message": {"id": "m2"}}]}], "historyId": "105"})
            return Response({"history": [{"id": "101", "messagesAdded": [{"message": {"id": "m1"}}]}, {"id": "102", "labelsAdded": [{"message": {"id": "m1"}, "labelIds": ["IMPORTANT"]}]}], "nextPageToken": "h2", "historyId": "103"})
        return Response(gmail_message(url.rsplit("/", 1)[-1], labels=["INBOX", "UNREAD"]))

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    result = client.post(f"/api/connections/{account_id}/sync", headers=headers).json()
    assert result["sync_type"] == "incremental"
    assert (result["added"], result["updated"], result["removed"]) == (2, 0, 0)
    assert result["status"] == "complete"
    assert len(history_calls) == 2
    assert history_calls[0]["startHistoryId"] == "100"
    assert history_calls[1]["pageToken"] == "h2"
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert account.gmail_history_id == "105"
        assert account.gmail_sync_baseline_history_id is None
        assert db.query(Email).filter_by(connected_account_id=account_id).count() == 2
        locally_modified = db.query(Email).filter_by(connected_account_id=account_id, provider_message_id="m2").one()
        locally_modified.is_read = True
        locally_modified.is_read_user_modified = True
        locally_modified.is_important = True
        locally_modified.is_important_user_modified = True
        locally_modified.category = "personal"
        db.commit()
    finally:
        db.close()

    # Replayed event IDs/messages do not create duplicate imports.
    monkeypatch.setattr(gmail_provider.httpx, "get", lambda url, params=None, **kwargs: Response(
        {"emailAddress": "owner@gmail.test", "historyId": "106"} if url.endswith("/profile") else {"history": [{"id": "105", "messagesAdded": [{"message": {"id": "m2"}}]}], "historyId": "106"} if url.endswith("/history") else gmail_message("m2")
    ))
    repeated = client.post(f"/api/connections/{account_id}/sync", headers=headers).json()
    assert repeated["added"] == 0 and repeated["updated"] == 1
    db = TestingSessionLocal()
    try:
        locally_modified = db.query(Email).filter_by(connected_account_id=account_id, provider_message_id="m2").one()
        assert db.query(Email).filter_by(connected_account_id=account_id, provider_message_id="m2").count() == 1
        assert locally_modified.is_read is True and locally_modified.is_important is True
        assert locally_modified.category == "personal"
    finally:
        db.close()


def test_history_deletion_soft_deletes_imported_email_only(client, monkeypatch):
    configure(monkeypatch)
    headers, user_id = register(client, "sync-delete-event@knit.app")
    account_id = add_account(user_id)
    db = TestingSessionLocal()
    try:
        db.query(ConnectedAccount).filter_by(id=account_id).update({ConnectedAccount.gmail_history_id: "200"})
        imported = Email(user_id=user_id, connected_account_id=account_id, provider_message_id="gone", provider_thread_id="thread-gone", sender_name="Gmail", sender_email="gmail@example.test", recipient="owner@gmail.test", subject="Imported", body="body", received_at=datetime.now(timezone.utc), category="other")
        db.add(imported)
        db.commit()
        imported_id = imported.id
    finally:
        db.close()

    def fake_get(url, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "201"})
        if url.endswith("/history"):
            return Response({"history": [{"id": "201", "messagesDeleted": [{"message": {"id": "gone"}}]}], "historyId": "202"})
        raise AssertionError("deleted messages must not be fetched")

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    result = client.post(f"/api/connections/{account_id}/sync", headers=headers).json()
    assert result["removed"] == 1
    db = TestingSessionLocal()
    try:
        email = db.query(Email).filter_by(id=imported_id).one()
        assert email.is_deleted is True
        assert db.query(Email).filter(Email.user_id == user_id, Email.connected_account_id.is_(None)).count() == 0
    finally:
        db.close()


def test_history_cursor_404_requires_full_resync_then_reconciles_missing_mail(client, monkeypatch):
    configure(monkeypatch)
    headers, user_id = register(client, "sync-expired-history@knit.app")
    account_id = add_account(user_id)
    db = TestingSessionLocal()
    try:
        db.query(ConnectedAccount).filter_by(id=account_id).update({ConnectedAccount.gmail_history_id: "expired"})
        stale = Email(user_id=user_id, connected_account_id=account_id, provider_message_id="stale", provider_thread_id="thread-stale", sender_name="Gmail", sender_email="gmail@example.test", recipient="owner@gmail.test", subject="Stale", body="body", received_at=datetime.now(timezone.utc), category="other")
        db.add(stale)
        db.commit()
        stale_id = stale.id
    finally:
        db.close()

    state = {"expired": True}
    def fake_get(url, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "300"})
        if url.endswith("/history"):
            return Response({}, 404)
        if url.endswith("/messages"):
            return Response({"messages": []})
        raise AssertionError("no message detail expected")

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    expired = client.post(f"/api/connections/{account_id}/sync", headers=headers).json()
    assert expired["error_code"] == "history_cursor_invalid"
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert account.gmail_history_id is None
        assert account.sync_status == "full_resync_required"
    finally:
        db.close()

    resynced = client.post(f"/api/connections/{account_id}/sync", headers=headers).json()
    assert resynced["sync_type"] == "initial" and resynced["status"] == "complete"
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert account.gmail_history_id == "300"
        stale_email = db.query(Email).filter_by(id=stale_id).one()
        assert stale_email.is_deleted is True
    finally:
        db.close()


def test_incremental_cursor_does_not_advance_after_partial_history_failure(client, monkeypatch):
    configure(monkeypatch)
    headers, user_id = register(client, "sync-history-partial@knit.app")
    account_id = add_account(user_id)
    db = TestingSessionLocal()
    try:
        db.query(ConnectedAccount).filter_by(id=account_id).update({ConnectedAccount.gmail_history_id: "400"})
        db.commit()
    finally:
        db.close()

    def first_get(url, params=None, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "401"})
        if url.endswith("/history"):
            if params.get("pageToken") == "second":
                return Response({}, 503)
            return Response({"history": [{"id": "401", "messagesAdded": [{"message": {"id": "page-one"}}]}], "nextPageToken": "second", "historyId": "401"})
        return Response(gmail_message("page-one"))

    monkeypatch.setattr(gmail_provider.httpx, "get", first_get)
    failed = client.post(f"/api/connections/{account_id}/sync", headers=headers).json()
    assert failed["status"] == "partial"
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert account.gmail_history_id == "400"
        assert account.gmail_sync_baseline_history_id == "400"
        assert account.gmail_sync_page_token == "second"
        assert db.query(Email).filter_by(connected_account_id=account_id, provider_message_id="page-one").count() == 1
    finally:
        db.close()


def test_initial_sync_page_count_is_bounded_and_resumable(client, monkeypatch):
    configure(monkeypatch, max_messages=2, page_size=1)
    headers, user_id = register(client, "sync-bounded-initial@knit.app")
    account_id = add_account(user_id)
    calls = []

    def fake_get(url, params=None, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "100"})
        if url.endswith("/history"):
            return Response({"history": [], "historyId": "100"})
        calls.append(params.get("pageToken"))
        return Response({"messages": [], "nextPageToken": f"page-{len(calls)}"})

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    response = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "initial_sync_pending"
    assert response.json()["limit_reached"] is True
    assert len(calls) == 2


def test_incremental_sync_page_count_is_bounded_and_cursor_is_not_advanced(client, monkeypatch):
    configure(monkeypatch, max_messages=2, page_size=1)
    headers, user_id = register(client, "sync-bounded-incremental@knit.app")
    account_id = add_account(user_id)
    db = TestingSessionLocal()
    try:
        db.query(ConnectedAccount).filter_by(id=account_id).update({ConnectedAccount.gmail_history_id: "100"})
        db.commit()
    finally:
        db.close()
    calls = []

    def fake_get(url, params=None, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "200"})
        calls.append(params.get("pageToken"))
        return Response({"history": [], "nextPageToken": f"history-{len(calls)}", "historyId": "200"})

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    response = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "incremental_sync_pending"
    assert response.json()["limit_reached"] is True
    assert len(calls) == 2
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert account.gmail_history_id == "100"
        assert account.gmail_sync_page_token == "history-2"
    finally:
        db.close()


def test_incremental_deletion_events_count_toward_per_run_limit(client, monkeypatch):
    configure(monkeypatch, max_messages=1, page_size=1)
    headers, user_id = register(client, "sync-bounded-deletes@knit.app")
    account_id = add_account(user_id)
    db = TestingSessionLocal()
    try:
        db.query(ConnectedAccount).filter_by(id=account_id).update({ConnectedAccount.gmail_history_id: "100"})
        db.commit()
    finally:
        db.close()

    def fake_get(url, params=None, **kwargs):
        if url.endswith("/profile"):
            return Response({"emailAddress": "owner@gmail.test", "historyId": "200"})
        return Response({"history": [{"id": "101", "messagesDeleted": [
            {"message": {"id": "gone-1"}}, {"message": {"id": "gone-2"}}
        ]}], "historyId": "200"})

    monkeypatch.setattr(gmail_provider.httpx, "get", fake_get)
    response = client.post(f"/api/connections/{account_id}/sync", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "incremental_sync_pending"
    assert response.json()["limit_reached"] is True
    db = TestingSessionLocal()
    try:
        account = db.query(ConnectedAccount).filter_by(id=account_id).one()
        assert account.gmail_history_id == "100"
    finally:
        db.close()
