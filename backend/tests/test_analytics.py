from contextlib import contextmanager
from datetime import datetime, time, timedelta, timezone

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.email import Email
from app.models.email_analysis import EmailAnalysis


def register_user(client: TestClient, email: str) -> tuple[str, int]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "strongpassword123", "full_name": "Analytics User"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    user_response = client.get("/api/auth/me", headers=auth(token))
    assert user_response.status_code == 200
    return token, user_response.json()["id"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@contextmanager
def database_session():
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        yield db
    finally:
        db_generator.close()


def user_email_ids(client: TestClient, token: str) -> list[int]:
    response = client.get("/api/emails?pageSize=100", headers=auth(token))
    assert response.status_code == 200
    return [item["id"] for item in response.json()["items"]]


def test_analytics_requires_authentication_and_scopes_data_to_user(client: TestClient):
    owner_token, owner_id = register_user(client, "analytics-owner@knit.app")
    other_token, _ = register_user(client, "analytics-other@knit.app")
    email_ids = user_email_ids(client, owner_token)

    deleted = client.delete(f"/api/emails/{email_ids[0]}", headers=auth(owner_token))
    task = client.post(
        "/api/tasks",
        headers=auth(owner_token),
        json={"title": "Owner-only task", "status": "pending"},
    )

    assert deleted.status_code == 200
    assert task.status_code == 201
    unauthenticated = client.get("/api/analytics/overview")
    owner = client.get("/api/analytics/overview", headers=auth(owner_token))
    other = client.get("/api/analytics/overview", headers=auth(other_token))

    assert unauthenticated.status_code == 401
    assert owner.status_code == 200
    assert other.status_code == 200
    assert owner.json()["emails"]["total"] == len(email_ids) - 1
    assert other.json()["emails"]["total"] == len(email_ids)
    assert owner.json()["tasks"]["total"] == 1
    assert other.json()["tasks"]["total"] == 0
    assert owner.json()["timezone"] == "UTC"
    assert len(owner.json()["email_activity"]) == 30


def test_analytics_counts_active_categories_separately_from_important_flag(client: TestClient):
    token, _ = register_user(client, "analytics-flags@knit.app")
    email_ids = user_email_ids(client, token)
    deleted = client.delete(f"/api/emails/{email_ids[0]}", headers=auth(token))
    assert deleted.status_code == 200

    response = client.get("/api/analytics/overview", headers=auth(token))
    email_counts = client.get("/api/emails/counts", headers=auth(token))
    assert response.status_code == 200
    assert email_counts.status_code == 200

    result = response.json()
    assert result["emails"]["total"] == email_counts.json()["all"]
    assert result["emails"]["unread"] == email_counts.json()["unread"]
    assert result["emails"]["important"] == email_counts.json()["important"]
    assert sum(category["count"] for category in result["email_categories"]) == result["emails"]["total"]


def test_email_activity_uses_30_utc_day_window_and_excludes_deleted_and_future_rows(client: TestClient, monkeypatch):
    token, user_id = register_user(client, "analytics-activity@knit.app")
    fixed_now = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("app.services.analytics.utc_now", lambda: fixed_now)
    email_ids = user_email_ids(client, token)
    start_day = fixed_now.date() - timedelta(days=29)
    start_at = datetime.combine(start_day, time.min, tzinfo=timezone.utc)

    with database_session() as db:
        records = db.query(Email).filter(Email.user_id == user_id).order_by(Email.id.asc()).all()
        for record in records:
            record.received_at = fixed_now - timedelta(days=60)
        records[0].received_at = start_at
        records[1].received_at = fixed_now
        records[2].received_at = start_at - timedelta(microseconds=1)
        records[3].received_at = fixed_now + timedelta(minutes=1)
        records[4].received_at = fixed_now
        records[4].is_deleted = True
        db.commit()

    response = client.get("/api/analytics/overview", headers=auth(token))
    assert response.status_code == 200
    result = response.json()
    by_date = {item["date"]: item["count"] for item in result["email_activity"]}
    assert result["activity_start"] == start_day.isoformat()
    assert result["activity_end"] == fixed_now.date().isoformat()
    assert by_date[start_day.isoformat()] == 1
    assert by_date[fixed_now.date().isoformat()] == 1
    assert sum(by_date.values()) == 2
    assert result["emails"]["total"] == len(email_ids) - 1


def test_task_deadline_counts_include_boundaries_and_exclude_completed_tasks(client: TestClient, monkeypatch):
    token, _ = register_user(client, "analytics-deadlines@knit.app")
    fixed_now = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("app.services.analytics.utc_now", lambda: fixed_now)
    deadlines = [
        (fixed_now - timedelta(seconds=1), "pending", "Overdue"),
        (fixed_now, "in_progress", "Due now"),
        (fixed_now + timedelta(days=7), "pending", "Due in seven days"),
        (fixed_now + timedelta(days=7, seconds=1), "pending", "Due later"),
        (fixed_now - timedelta(days=1), "completed", "Completed task"),
    ]
    for due_at, status, title in deadlines:
        created = client.post(
            "/api/tasks",
            headers=auth(token),
            json={"title": title, "due_at": due_at.isoformat(), "status": status},
        )
        assert created.status_code == 201

    response = client.get("/api/analytics/overview", headers=auth(token))
    assert response.status_code == 200
    result = response.json()
    assert result["tasks"]["total"] == 5
    assert result["tasks"]["pending"] == 3
    assert result["tasks"]["in_progress"] == 1
    assert result["tasks"]["completed"] == 1
    assert result["tasks"]["overdue"] == 1
    assert result["tasks"]["due_next_7_days"] == 2
    assert [task["title"] for task in result["upcoming_deadlines"]] == [
        "Due now", "Due in seven days", "Due later",
    ]


def test_zero_data_and_missing_cached_analysis_return_graceful_empty_values(client: TestClient):
    token, _ = register_user(client, "analytics-empty@knit.app")
    email_ids = user_email_ids(client, token)
    for email_id in email_ids:
        response = client.delete(f"/api/emails/{email_id}", headers=auth(token))
        assert response.status_code == 200

    result = client.get("/api/analytics/overview", headers=auth(token))
    assert result.status_code == 200
    data = result.json()
    assert data["emails"] == {"total": 0, "unread": 0, "important": 0}
    assert data["tasks"]["total"] == 0
    assert all(category["count"] == 0 for category in data["email_categories"])
    assert len(data["email_activity"]) == 30
    assert all(day["count"] == 0 for day in data["email_activity"])
    assert data["upcoming_deadlines"] == []
    assert data["recent_activity"] == []
    assert data["ai_insights"] == {"analysis_count": 0, "high_risk_flag_count": 0}


def test_ai_insights_use_only_cached_analysis_for_active_owned_email(client: TestClient):
    token, user_id = register_user(client, "analytics-cached-ai@knit.app")
    email_ids = user_email_ids(client, token)
    client.delete(f"/api/emails/{email_ids[1]}", headers=auth(token))

    with database_session() as db:
        active = db.query(Email).filter(Email.id == email_ids[0], Email.user_id == user_id).one()
        deleted = db.query(Email).filter(Email.id == email_ids[1], Email.user_id == user_id).one()
        for email in (active, deleted):
            db.add(EmailAnalysis(
                user_id=user_id,
                email_id=email.id,
                suggested_category="Other",
                category_confidence=0.5,
                category_explanation="Cached test analysis.",
                summary="Cached summary.",
                main_purpose="Cached purpose.",
                important_points=[],
                required_action=None,
                relevant_dates=[],
                extracted={},
                security_risk="High",
                security_warning_signs=[],
                security_explanation="Cached risk assessment.",
                model_name="mock-model",
            ))
        db.commit()

    response = client.get("/api/analytics/overview", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["ai_insights"] == {"analysis_count": 1, "high_risk_flag_count": 1}
