from types import SimpleNamespace
from unittest.mock import Mock

from app.core.config import settings
from app.schemas.assistant import AssistantProviderOutput
from app.schemas.reply import ReplyProviderOutput
from app.services import gemini


def test_ai_connection_endpoint_requires_auth_and_returns_safe_status(client):
    assert client.get("/api/ai/connection").status_code == 401


def test_create_gemini_client_uses_bounded_retries(monkeypatch):
    from google import genai
    from google.genai import types

    client = Mock()
    options = {}

    def fake_http_options(**kwargs):
        options.update(kwargs)
        return kwargs

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "unit-test-key")
    monkeypatch.setattr(settings, "GEMINI_TIMEOUT_SECONDS", 17)
    monkeypatch.setattr(types, "HttpOptions", fake_http_options)
    monkeypatch.setattr(genai, "Client", Mock(return_value=client))

    assert gemini._create_gemini_client() is client
    assert options["timeout"] == 17000
    retry_options = options["retry_options"]
    assert retry_options.attempts == 2
    assert retry_options.initial_delay == 0.5
    assert retry_options.max_delay == 2.0
    assert retry_options.http_status_codes == [408, 429, 500, 502, 503, 504]


def test_ping_gemini_text_sends_plain_text_without_json_config(monkeypatch):
    expected_text = "KNIT CONNECTION OK"
    response = SimpleNamespace(text=expected_text)
    client = SimpleNamespace(models=SimpleNamespace(generate_content=Mock(return_value=response)))
    config_args = {}

    def fake_config(**kwargs):
        config_args.update(kwargs)
        return kwargs

    from google.genai import types

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "unit-test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.5-flash")
    monkeypatch.setattr(gemini, "_create_gemini_client", lambda: client)
    monkeypatch.setattr(types, "GenerateContentConfig", fake_config)

    result = gemini.ping_gemini_text()

    assert result == expected_text
    client.models.generate_content.assert_called_once_with(
        model="gemini-3.5-flash",
        contents="Reply with exactly: KNIT CONNECTION OK",
        config={"temperature": 0.1},
    )
    assert "response_mime_type" not in config_args
    assert "response_schema" not in config_args


def test_assistant_provider_uses_shared_client_and_validated_json(monkeypatch):
    prompt = "mocked assistant prompt"
    response = SimpleNamespace(
        text='{"answer":"There are two relevant emails.","source_email_ids":[1,2]}'
    )
    client = SimpleNamespace(models=SimpleNamespace(generate_content=Mock(return_value=response)))
    config_args = {}

    def fake_config(**kwargs):
        config_args.update(kwargs)
        return kwargs

    from google.genai import types

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "unit-test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.5-flash")
    monkeypatch.setattr(gemini, "_create_gemini_client", Mock(return_value=client))
    monkeypatch.setattr(types, "GenerateContentConfig", fake_config)

    result = gemini.generate_assistant_answer_with_gemini(prompt)

    assert result == AssistantProviderOutput(
        answer="There are two relevant emails.",
        source_email_ids=[1, 2],
    )
    gemini._create_gemini_client.assert_called_once_with()
    client.models.generate_content.assert_called_once_with(
        model="gemini-3.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AssistantProviderOutput,
            "temperature": 0.1,
        },
    )
    assert config_args["response_schema"] is AssistantProviderOutput


def test_safe_provider_error_omits_raw_provider_message():
    response = SimpleNamespace(headers={"x-goog-request-id": "request-123"})
    provider_exception = type(
        "FakeApiError",
        (Exception,),
        {"code": 503, "response": response},
    )("provider returned sensitive detail")

    error = gemini._safe_provider_error(provider_exception)

    assert error.kind == "upstream"
    assert error.status_code == 503
    assert error.exception_type == "FakeApiError"
    assert error.safe_message == "Gemini provider request failed with HTTP status 503."
    assert error.request_id == "request-123"
    assert "sensitive detail" not in str(error)
    assert "sensitive detail" not in error.safe_message


def test_reply_provider_uses_shared_client_and_validated_json(monkeypatch):
    prompt = "mocked reply prompt"
    response = SimpleNamespace(text='{"reply_body":"Thank you for your message."}')
    client = SimpleNamespace(models=SimpleNamespace(generate_content=Mock(return_value=response)))
    config_args = {}

    def fake_config(**kwargs):
        config_args.update(kwargs)
        return kwargs

    from google.genai import types

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "unit-test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.5-flash")
    monkeypatch.setattr(gemini, "_create_gemini_client", Mock(return_value=client))
    monkeypatch.setattr(types, "GenerateContentConfig", fake_config)

    result = gemini.generate_reply_with_gemini(prompt)

    assert result == "Thank you for your message."
    gemini._create_gemini_client.assert_called_once_with()
    client.models.generate_content.assert_called_once_with(
        model="gemini-3.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ReplyProviderOutput,
            "temperature": 0.2,
        },
    )
    assert config_args["response_schema"] is ReplyProviderOutput
