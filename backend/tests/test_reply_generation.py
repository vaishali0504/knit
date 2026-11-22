import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.config import settings


def register_user(client, email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "strongpassword123", "full_name": "Reply Test User"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def first_email_id(client, token: str) -> int:
    response = client.get("/api/emails?pageSize=1", headers=auth(token))
    assert response.status_code == 200
    return response.json()["items"][0]["id"]


def test_reply_generation_uses_owned_email_and_optional_cached_analysis(client, monkeypatch):
    token = register_user(client, "reply-context@knit.app")
    email_id = first_email_id(client, token)
    email = client.get(f"/api/emails/{email_id}", headers=auth(token)).json()
    captured = {}
    analysis = SimpleNamespace(
        main_purpose="Request a response about an interview.",
        summary="A fictional recruiter asks about interview availability.",
        important_points=["The sender requested a reply."],
        required_action="Share availability if known.",
        relevant_dates=["2027-03-10"],
        extracted={"company": "Northstar Labs", "role": "Intern"},
    )

    def mocked_provider(prompt: str) -> str:
        captured["prompt"] = prompt
        return "Thank you for reaching out. Could you share more details?"

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock-key")
    monkeypatch.setattr("app.services.reply_generation.generate_reply_with_gemini", mocked_provider)
    monkeypatch.setattr(
        "app.services.reply_generation.analysis_repo.get_for_email",
        lambda db, user_id, requested_email_id: analysis,
    )

    response = client.post(
        f"/api/ai/emails/{email_id}/reply",
        headers=auth(token),
        json={"tone": "friendly"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "email_id": email_id,
        "tone": "friendly",
        "reply_body": "Thank you for reaching out. Could you share more details?",
    }
    prompt = captured["prompt"]
    assert email["subject"] in prompt
    assert email["body"].splitlines()[2] in prompt
    assert email["sender_email"] in prompt
    assert email["recipient"] in prompt
    assert "Northstar Labs" in prompt
    assert "Request a response about an interview." in prompt
    assert "untrusted data" in prompt
    assert "Do not invent" in prompt


def test_reply_generation_works_without_cached_analysis(client, monkeypatch):
    token = register_user(client, "reply-no-analysis@knit.app")
    email_id = first_email_id(client, token)
    captured = {}

    def mocked_provider(prompt: str) -> str:
        captured["prompt"] = prompt
        return "Thank you for the information."

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock-key")
    monkeypatch.setattr("app.services.reply_generation.generate_reply_with_gemini", mocked_provider)

    response = client.post(
        f"/api/ai/emails/{email_id}/reply",
        headers=auth(token),
        json={"tone": "professional"},
    )

    assert response.status_code == 200
    context = json.loads(captured["prompt"].split("UNTRUSTED EMAIL CONTEXT (JSON):\n", 1)[1])
    assert context["cached_analysis_if_available"] is None
    assert context["received_content"]


def test_reply_generation_requires_authentication_and_email_ownership(client, monkeypatch):
    owner_token = register_user(client, "reply-owner@knit.app")
    other_token = register_user(client, "reply-other@knit.app")
    email_id = first_email_id(client, owner_token)
    provider = Mock(return_value="Mock reply")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock-key")
    monkeypatch.setattr("app.services.reply_generation.generate_reply_with_gemini", provider)

    unauthenticated = client.post(
        f"/api/ai/emails/{email_id}/reply", json={"tone": "formal"}
    )
    cross_user = client.post(
        f"/api/ai/emails/{email_id}/reply",
        headers=auth(other_token),
        json={"tone": "formal"},
    )

    assert unauthenticated.status_code == 401
    assert cross_user.status_code == 404
    provider.assert_not_called()


def test_reply_generation_rejects_unsupported_tone(client, monkeypatch):
    token = register_user(client, "reply-tone@knit.app")
    email_id = first_email_id(client, token)
    provider = Mock(return_value="Mock reply")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock-key")
    monkeypatch.setattr("app.services.reply_generation.generate_reply_with_gemini", provider)

    response = client.post(
        f"/api/ai/emails/{email_id}/reply",
        headers=auth(token),
        json={"tone": "sarcastic"},
    )

    assert response.status_code == 422
    provider.assert_not_called()


@pytest.mark.parametrize("tone", ["professional", "friendly", "formal", "short_direct"])
def test_reply_generation_accepts_all_supported_tones(client, monkeypatch, tone):
    token = register_user(client, f"reply-tone-{tone}@knit.app")
    email_id = first_email_id(client, token)
    provider = Mock(return_value="Mock reply")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock-key")
    monkeypatch.setattr("app.services.reply_generation.generate_reply_with_gemini", provider)

    response = client.post(
        f"/api/ai/emails/{email_id}/reply",
        headers=auth(token),
        json={"tone": tone},
    )

    assert response.status_code == 200
    assert response.json()["tone"] == tone
    provider.assert_called_once()


def test_saved_reply_draft_persists_and_updates_once_per_user_email(client):
    token = register_user(client, "reply-draft@knit.app")
    email_id = first_email_id(client, token)
    headers = auth(token)
    draft_path = f"/api/ai/emails/{email_id}/reply-draft"

    missing = client.get(draft_path, headers=headers)
    first = client.put(
        draft_path,
        headers=headers,
        json={"tone": "professional", "content": "Initial edited reply."},
    )
    updated = client.put(
        draft_path,
        headers=headers,
        json={"tone": "short_direct", "content": "Updated edited reply."},
    )
    loaded = client.get(draft_path, headers=headers)

    assert missing.status_code == 200 and missing.json() is None
    assert first.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["id"] == first.json()["id"]
    assert updated.json()["tone"] == "short_direct"
    assert updated.json()["content"] == "Updated edited reply."
    assert loaded.json()["id"] == first.json()["id"]
    assert loaded.json()["content"] == "Updated edited reply."


def test_reply_draft_access_is_authenticated_and_email_scoped(client):
    owner_token = register_user(client, "reply-draft-owner@knit.app")
    other_token = register_user(client, "reply-draft-other@knit.app")
    email_id = first_email_id(client, owner_token)
    draft_path = f"/api/ai/emails/{email_id}/reply-draft"

    saved = client.put(
        draft_path,
        headers=auth(owner_token),
        json={"tone": "friendly", "content": "Owner's draft."},
    )
    get_other = client.get(draft_path, headers=auth(other_token))
    put_other = client.put(
        draft_path,
        headers=auth(other_token),
        json={"tone": "formal", "content": "Unauthorized update."},
    )
    get_unauthenticated = client.get(draft_path)

    assert saved.status_code == 200
    assert get_other.status_code == 404
    assert put_other.status_code == 404
    assert get_unauthenticated.status_code == 401


def test_reply_provider_failure_maps_to_controlled_api_error(client, monkeypatch):
    from app.services.gemini import GeminiProviderError

    token = register_user(client, "reply-provider-error@knit.app")
    email_id = first_email_id(client, token)

    def mocked_provider(prompt: str) -> str:
        raise GeminiProviderError("rate_limit", 429)

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock-key")
    monkeypatch.setattr("app.services.reply_generation.generate_reply_with_gemini", mocked_provider)

    response = client.post(
        f"/api/ai/emails/{email_id}/reply",
        headers=auth(token),
        json={"tone": "professional"},
    )

    assert response.status_code == 429
    assert "rate limit" in response.json()["detail"].lower()
