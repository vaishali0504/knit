from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.models.email import Email
from conftest import TestingSessionLocal

from app.core.config import settings
from app.schemas.ai import AIAnalysisOutput


def register_user(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "strongpassword123", "full_name": "AI Test User"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def add_test_email(token: str, client: TestClient) -> dict:
    user = client.get("/api/auth/me", headers=headers(token))
    assert user.status_code == 200
    db = TestingSessionLocal()
    try:
        email = Email(
            user_id=user.json()["id"],
            sender_name="NovaTech University Recruiting",
            sender_email="recruiting@novatech.test",
            recipient=user.json()["email"],
            subject="Internship application received",
            body="Please submit your unofficial transcript.",
            received_at=datetime.now(timezone.utc),
            category="internship",
            is_read=False,
            is_important=True,
        )
        db.add(email)
        db.commit()
        db.refresh(email)
        return {"id": email.id}
    finally:
        db.close()


def mock_analysis() -> AIAnalysisOutput:
    return AIAnalysisOutput.model_validate({
        "classification": {
            "category": "Internship",
            "confidence": 0.91,
            "explanation": "The sender describes an internship application.",
        },
        "summary": {
            "short_summary": "A fictional recruiting team confirms an internship application.",
            "main_purpose": "Communicate application status.",
            "important_points": ["An application was received."],
            "required_action": "Submit the requested unofficial transcript.",
            "relevant_dates": ["Summer 2027"],
        },
        "extracted": {
            "person_or_organization": "NovaTech University Recruiting",
            "company": "NovaTech",
            "role": "Software Engineering Intern",
            "skills": ["React"],
            "eligibility": [],
            "stipend_or_compensation": None,
            "application_deadline": None,
            "interview_date_time": None,
            "event_date": None,
            "event_location": None,
            "application_or_registration_url": "https://example.invalid/application",
            "required_documents": ["Unofficial transcript"],
            "contact_information": "recruiting@novatech.example",
            "next_action": "Submit documents.",
        },
        "security": {
            "risk_level": "Low",
            "warning_signs": [],
            "explanation": "No suspicious indicators were detected in this fictional email.",
        },
    })


def test_missing_gemini_key_returns_configuration_message(client: TestClient, monkeypatch):
    token = register_user(client, "missing-ai-key@knit.app")
    email_id = add_test_email(token, client)["id"]
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    response = client.post(f"/api/ai/emails/{email_id}/analyze", headers=headers(token))
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_mocked_analysis_is_cached_and_manual_category_persists(client: TestClient, monkeypatch):
    token = register_user(client, "mock-ai@knit.app")
    email_id = add_test_email(token, client)["id"]
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "test-model")

    calls = {"count": 0}

    def mocked_gemini(*args, **kwargs):
        calls["count"] += 1
        return mock_analysis()

    monkeypatch.setattr("app.services.ai_analysis.analyze_email_with_gemini", mocked_gemini)

    first = client.post(f"/api/ai/emails/{email_id}/analyze", headers=headers(token))
    assert first.status_code == 200
    data = first.json()
    assert data["suggested_category"] == "Internship"
    assert 0.0 <= data["category_confidence"] <= 1.0
    assert data["effective_category"] == "Internship"
    assert data["cached"] is False

    second = client.post(f"/api/ai/emails/{email_id}/analyze", headers=headers(token))
    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert calls["count"] == 1

    corrected = client.patch(
        f"/api/ai/emails/{email_id}/category",
        json={"category": "Important"},
        headers=headers(token),
    )
    assert corrected.status_code == 200
    assert corrected.json()["manual_category"] == "Important"
    assert corrected.json()["effective_category"] == "Important"

    regenerated = client.post(
        f"/api/ai/emails/{email_id}/analyze?regenerate=true",
        headers=headers(token),
    )
    assert regenerated.status_code == 200
    assert regenerated.json()["manual_category"] == "Important"
    assert regenerated.json()["effective_category"] == "Important"
    assert calls["count"] == 2


def test_ai_analysis_requires_ownership(client: TestClient, monkeypatch):
    token_a = register_user(client, "ai-owner-a@knit.app")
    token_b = register_user(client, "ai-owner-b@knit.app")
    email_a = add_test_email(token_a, client)

    response = client.post(
        f"/api/ai/emails/{email_a['id']}/analyze",
        headers=headers(token_b),
    )
    assert response.status_code in (404, 503)


def test_default_model_is_new_configured_model():
    assert settings.GEMINI_MODEL == "gemini-3.5-flash"


def test_provider_rate_limit_is_controlled(client: TestClient, monkeypatch):
    token = register_user(client, "rate-limit-ai@knit.app")
    email_id = add_test_email(token, client)["id"]
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")

    def mocked_gemini(*args, **kwargs):
        from app.services.gemini import GeminiProviderError
        raise GeminiProviderError("rate_limit", 429)

    monkeypatch.setattr("app.services.ai_analysis.analyze_email_with_gemini", mocked_gemini)
    response = client.post(f"/api/ai/emails/{email_id}/analyze", headers=headers(token))
    assert response.status_code == 429
    assert "rate limit" in response.json()["detail"].lower()


def test_provider_upstream_failure_is_controlled(client: TestClient, monkeypatch):
    token = register_user(client, "upstream-ai@knit.app")
    email_id = add_test_email(token, client)["id"]
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")

    def mocked_gemini(*args, **kwargs):
        from app.services.gemini import GeminiProviderError
        raise GeminiProviderError("upstream", 404)

    monkeypatch.setattr("app.services.ai_analysis.analyze_email_with_gemini", mocked_gemini)
    response = client.post(f"/api/ai/emails/{email_id}/analyze", headers=headers(token))
    assert response.status_code == 502
    assert "temporarily unavailable" in response.json()["detail"].lower()
