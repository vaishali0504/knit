from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.models.email import Email
from conftest import TestingSessionLocal


def register_user(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "strongpassword123", "full_name": "Demo User"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def add_test_email(client: TestClient, token: str, subject: str = "Interview invitation", category: str = "interview", important: bool = False, read: bool = False) -> int:
    me = client.get("/api/auth/me", headers=auth_headers(token))
    assert me.status_code == 200
    user_id = me.json()["id"]
    db = TestingSessionLocal()
    try:
        email = Email(
            user_id=user_id,
            sender_name="Test Sender",
            sender_email="sender@example.test",
            recipient="owner@knit.app",
            subject=subject,
            body="Please review this interview information.",
            received_at=datetime.now(timezone.utc),
            category=category,
            is_read=read,
            is_important=important,
            is_deleted=False,
        )
        db.add(email)
        db.commit()
        db.refresh(email)
        return email.id
    finally:
        db.close()


def test_new_user_starts_with_empty_real_mailbox(client: TestClient):
    token = register_user(client, "inbox-owner@knit.app")
    response = client.get("/api/emails", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert all(item["category"] in {
        "internship", "interview", "college", "important", "personal",
        "promotions", "updates", "suspicious", "other"
    } for item in data["items"])


def test_category_filters_and_counts(client: TestClient):
    token = register_user(client, "filters-owner@knit.app")
    headers = auth_headers(token)
    add_test_email(client, token, category="internship", important=True)
    add_test_email(client, token, category="suspicious")
    add_test_email(client, token, category="other")

    internship = client.get("/api/emails?category=internship", headers=headers)
    assert internship.status_code == 200
    assert internship.json()["total"] >= 1
    assert all(item["category"] == "internship" for item in internship.json()["items"])

    counts = client.get("/api/emails/counts", headers=headers)
    assert counts.status_code == 200
    assert counts.json()["internship"] >= 1
    assert counts.json()["suspicious"] >= 1
    assert counts.json()["other"] >= 1


def test_important_filter_uses_important_flag(client: TestClient):
    token = register_user(client, "important-owner@knit.app")
    headers = auth_headers(token)
    add_test_email(client, token, important=True)
    response = client.get("/api/emails?category=important", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    assert all(item["is_important"] is True for item in response.json()["items"])


def test_search_read_filter_and_sorting(client: TestClient):
    token = register_user(client, "search-owner@knit.app")
    headers = auth_headers(token)
    add_test_email(client, token, subject="Interview invitation")
    add_test_email(client, token, subject="Older invitation", read=True)

    search = client.get("/api/emails?search=interview", headers=headers)
    assert search.status_code == 200
    assert search.json()["total"] >= 1

    unread = client.get("/api/emails?status=unread", headers=headers)
    assert unread.status_code == 200
    assert all(item["is_read"] is False for item in unread.json()["items"])

    newest = client.get("/api/emails?sort=newest&pageSize=1", headers=headers)
    oldest = client.get("/api/emails?sort=oldest&pageSize=1", headers=headers)
    assert newest.status_code == 200
    assert oldest.status_code == 200
    assert newest.json()["items"][0]["received_at"] >= oldest.json()["items"][0]["received_at"]


def test_open_email_marks_read_and_actions_persist(client: TestClient):
    token = register_user(client, "actions-owner@knit.app")
    headers = auth_headers(token)
    add_test_email(client, token, read=False)

    unread = client.get("/api/emails?status=unread&pageSize=1", headers=headers)
    email_id = unread.json()["items"][0]["id"]

    detail = client.get(f"/api/emails/{email_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["is_read"] is True

    important = client.patch(f"/api/emails/{email_id}/important", headers=headers)
    assert important.status_code == 200
    assert important.json()["is_important"] is True

    removed = client.patch(f"/api/emails/{email_id}/unimportant", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["is_important"] is False

    unread_action = client.patch(f"/api/emails/{email_id}/unread", headers=headers)
    assert unread_action.status_code == 200
    assert unread_action.json()["is_read"] is False


def test_delete_restore_and_permanent_delete(client: TestClient):
    token = register_user(client, "delete-owner@knit.app")
    headers = auth_headers(token)
    add_test_email(client, token)
    email_id = client.get("/api/emails?pageSize=1", headers=headers).json()["items"][0]["id"]

    deleted = client.delete(f"/api/emails/{email_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_deleted"] is True

    trash = client.get("/api/emails?deleted=true", headers=headers)
    assert trash.status_code == 200
    assert any(item["id"] == email_id for item in trash.json()["items"])

    restored = client.post(f"/api/emails/{email_id}/restore", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["is_deleted"] is False

    client.delete(f"/api/emails/{email_id}", headers=headers)
    permanent = client.delete(f"/api/emails/{email_id}/permanent", headers=headers)
    assert permanent.status_code == 204


def test_email_ownership_isolation(client: TestClient):
    token_a = register_user(client, "owner-a@knit.app")
    token_b = register_user(client, "owner-b@knit.app")
    add_test_email(client, token_a)
    add_test_email(client, token_b)

    email_a = client.get("/api/emails?pageSize=1", headers=auth_headers(token_a)).json()["items"][0]
    email_b = client.get("/api/emails?pageSize=1", headers=auth_headers(token_b)).json()["items"][0]
    assert email_a["id"] != email_b["id"]

    response = client.get(
        f"/api/emails/{email_a['id']}",
        headers=auth_headers(token_b),
    )
    assert response.status_code == 404

    delete_response = client.delete(
        f"/api/emails/{email_a['id']}",
        headers=auth_headers(token_b),
    )
    assert delete_response.status_code == 404


def test_inbox_requires_authentication(client: TestClient):
    response = client.get("/api/emails")
    assert response.status_code in (401, 403)
