from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def register_user(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "strongpassword123", "full_name": "Task User"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_list_update_complete_and_delete_task(client: TestClient):
    token = register_user(client, "task-owner@knit.app")
    headers = auth_headers(token)
    payload = {
        "title": "Submit transcript",
        "description": "Upload the requested unofficial transcript.",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "priority": "high",
        "status": "pending",
    }

    created = client.post("/api/tasks", json=payload, headers=headers)
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == payload["title"]
    assert task["priority"] == "high"
    assert task["status"] == "pending"

    listed = client.get("/api/tasks", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == task["id"]

    updated = client.patch(
        f"/api/tasks/{task['id']}",
        json={"status": "in_progress", "description": "Updated description"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "in_progress"

    completed = client.patch(
        f"/api/tasks/{task['id']}",
        json={"status": "completed"},
        headers=headers,
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["completed_at"] is not None

    deleted = client.delete(f"/api/tasks/{task['id']}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/tasks/{task['id']}", headers=headers).status_code == 404


def test_task_filters_search_sort_and_counts(client: TestClient):
    token = register_user(client, "task-filter@knit.app")
    headers = auth_headers(token)

    due = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    client.post(
        "/api/tasks",
        json={"title": "Review interview invitation", "due_at": due, "priority": "high", "status": "pending"},
        headers=headers,
    )
    client.post(
        "/api/tasks",
        json={"title": "Read course update", "priority": "low", "status": "completed"},
        headers=headers,
    )

    filtered = client.get("/api/tasks?status=pending&priority=high&search=interview", headers=headers)
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["title"] == "Review interview invitation"

    counts = client.get("/api/tasks/counts", headers=headers)
    assert counts.status_code == 200
    assert counts.json()["all"] == 2
    assert counts.json()["pending"] == 1
    assert counts.json()["completed"] == 1
    assert counts.json()["upcoming"] == 1


def test_task_source_email_must_belong_to_user(client: TestClient):
    token_a = register_user(client, "task-owner-a@knit.app")
    token_b = register_user(client, "task-owner-b@knit.app")
    headers_a = auth_headers(token_a)
    headers_b = auth_headers(token_b)

    email_a = client.get("/api/emails?pageSize=1", headers=headers_a).json()["items"][0]
    response = client.post(
        "/api/tasks",
        json={"title": "Linked task", "source_email_id": email_a["id"]},
        headers=headers_b,
    )
    assert response.status_code == 404


def test_task_ownership_isolation(client: TestClient):
    token_a = register_user(client, "task-owner-isolation-a@knit.app")
    token_b = register_user(client, "task-owner-isolation-b@knit.app")
    headers_a = auth_headers(token_a)
    headers_b = auth_headers(token_b)

    created = client.post(
        "/api/tasks",
        json={"title": "Private task", "priority": "medium", "status": "pending"},
        headers=headers_a,
    )
    task_id = created.json()["id"]

    assert client.get(f"/api/tasks/{task_id}", headers=headers_b).status_code == 404
    assert client.patch(f"/api/tasks/{task_id}", json={"title": "Changed"}, headers=headers_b).status_code == 404
    assert client.delete(f"/api/tasks/{task_id}", headers=headers_b).status_code == 404


def test_invalid_task_values_and_unauthenticated_requests(client: TestClient):
    response = client.post(
        "/api/tasks",
        json={"title": "Invalid status", "status": "blocked"},
    )
    assert response.status_code in (401, 403)

    token = register_user(client, "task-validation@knit.app")
    headers = auth_headers(token)
    invalid_status = client.get("/api/tasks?status=blocked", headers=headers)
    assert invalid_status.status_code == 422

    invalid_priority = client.post(
        "/api/tasks",
        json={"title": "Invalid priority", "priority": "urgent"},
        headers=headers,
    )
    assert invalid_priority.status_code == 422
