import pytest
from cryptography.fernet import Fernet
from pydantic import ValidationError

from app.core.config import Settings


READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


def test_gmail_configuration_disabled_by_default():
    settings = Settings(_env_file=None)
    assert settings.GMAIL_INTEGRATION_ENABLED is False
    assert settings.GMAIL_OAUTH_SCOPES == [READONLY_SCOPE]


def test_ai_studio_environment_names_map_to_existing_settings():
    encryption_key = Fernet.generate_key().decode("ascii")
    settings = Settings(
        _env_file=None,
        JWT_SECRET_KEY="panel-jwt-secret-that-is-long-enough-123",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=45,
        TOKEN_ENCRYPTION_KEY=encryption_key,
        GOOGLE_CLIENT_ID="client-id",
        GOOGLE_CLIENT_SECRET="client-secret",
        GMAIL_REDIRECT_URI="http://127.0.0.1:8000/api/connections/gmail/callback",
        ALLOWED_ORIGINS=["https://app.example.test"],
        FRONTEND_URL="https://app.example.test",
        GMAIL_INTEGRATION_ENABLED=True,
    )

    assert settings.SECRET_KEY == "panel-jwt-secret-that-is-long-enough-123"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 45
    assert settings.GMAIL_TOKEN_ENCRYPTION_KEY == encryption_key
    assert settings.GOOGLE_OAUTH_CLIENT_ID == "client-id"
    assert settings.GOOGLE_OAUTH_CLIENT_SECRET == "client-secret"
    assert settings.GOOGLE_OAUTH_REDIRECT_URI == "http://127.0.0.1:8000/api/connections/gmail/callback"
    assert settings.CORS_ORIGINS == ["https://app.example.test"]


def test_ai_studio_environment_variables_are_loaded(monkeypatch):
    encryption_key = Fernet.generate_key().decode("ascii")
    values = {
        "ENVIRONMENT": "development",
        "GMAIL_INTEGRATION_ENABLED": "true",
        "JWT_SECRET_KEY": "panel-jwt-secret-that-is-long-enough-123",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "45",
        "TOKEN_ENCRYPTION_KEY": encryption_key,
        "GOOGLE_CLIENT_ID": "client-id",
        "GOOGLE_CLIENT_SECRET": "client-secret",
        "GMAIL_REDIRECT_URI": "http://127.0.0.1:8000/api/connections/gmail/callback",
        "ALLOWED_ORIGINS": '["https://app.example.test"]',
        "FRONTEND_URL": "https://app.example.test",
    }
    for name in (
        "SECRET_KEY",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "GMAIL_TOKEN_ENCRYPTION_KEY",
        "GOOGLE_OAUTH_CLIENT_ID",
        "GOOGLE_OAUTH_CLIENT_SECRET",
        "GOOGLE_OAUTH_REDIRECT_URI",
        "CORS_ORIGINS",
    ):
        monkeypatch.delenv(name, raising=False)
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    settings = Settings(_env_file=None)

    assert settings.SECRET_KEY == values["JWT_SECRET_KEY"]
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 45
    assert settings.GMAIL_TOKEN_ENCRYPTION_KEY == encryption_key
    assert settings.GOOGLE_OAUTH_CLIENT_ID == "client-id"
    assert settings.GOOGLE_OAUTH_CLIENT_SECRET == "client-secret"
    assert settings.GOOGLE_OAUTH_REDIRECT_URI == values["GMAIL_REDIRECT_URI"]
    assert settings.CORS_ORIGINS == ["https://app.example.test"]


def test_frontend_url_is_added_to_cors_origins():
    settings = Settings(
        _env_file=None,
        FRONTEND_URL="https://app.example.test",
        CORS_ORIGINS=["https://api-client.example.test"],
    )

    assert settings.CORS_ORIGINS == [
        "https://api-client.example.test",
        "https://app.example.test",
    ]


def test_sqlite_db_path_is_ignored_in_favor_of_database_url():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="sqlite:///./knit.db",
        SQLITE_DB_PATH="another-database.db",
    )

    assert settings.DATABASE_URL == "sqlite:///./knit.db"
    assert "SQLITE_DB_PATH" not in Settings.model_fields


def test_enabled_gmail_requires_backend_credentials_and_encryption_key():
    with pytest.raises(ValidationError, match="required configuration is missing"):
        Settings(_env_file=None, GMAIL_INTEGRATION_ENABLED=True)


def test_enabled_gmail_rejects_broader_scope():
    with pytest.raises(ValidationError, match="only the Gmail read-only scope"):
        Settings(
            _env_file=None,
            GMAIL_INTEGRATION_ENABLED=True,
            GOOGLE_OAUTH_CLIENT_ID="client-id",
            GOOGLE_OAUTH_CLIENT_SECRET="client-secret",
            GOOGLE_OAUTH_REDIRECT_URI="http://127.0.0.1:8000/api/connections/gmail/callback",
            GMAIL_TOKEN_ENCRYPTION_KEY=Fernet.generate_key().decode("ascii"),
            GMAIL_OAUTH_SCOPES=[READONLY_SCOPE, "https://www.googleapis.com/auth/gmail.modify"],
        )


def test_enabled_gmail_accepts_complete_development_configuration():
    settings = Settings(
        _env_file=None,
        GMAIL_INTEGRATION_ENABLED=True,
        GOOGLE_OAUTH_CLIENT_ID="client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="client-secret",
        GOOGLE_OAUTH_REDIRECT_URI="http://127.0.0.1:8000/api/connections/gmail/callback",
        GMAIL_TOKEN_ENCRYPTION_KEY=Fernet.generate_key().decode("ascii"),
    )
    assert settings.GMAIL_INTEGRATION_ENABLED is True
    assert settings.GMAIL_OAUTH_SCOPES == [READONLY_SCOPE]


def test_enabled_gmail_rejects_http_redirect_outside_development():
    with pytest.raises(ValidationError, match="must use HTTPS"):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            SECRET_KEY="unit-test-production-secret-key-0123456789abcdef",
            GMAIL_INTEGRATION_ENABLED=True,
            GOOGLE_OAUTH_CLIENT_ID="client-id",
            GOOGLE_OAUTH_CLIENT_SECRET="client-secret",
            GOOGLE_OAUTH_REDIRECT_URI="http://example.com/callback",
            GMAIL_TOKEN_ENCRYPTION_KEY=Fernet.generate_key().decode("ascii"),
        )


def test_enabled_gmail_rejects_invalid_token_encryption_key():
    with pytest.raises(ValidationError, match="valid Fernet key"):
        Settings(
            _env_file=None,
            GMAIL_INTEGRATION_ENABLED=True,
            GOOGLE_OAUTH_CLIENT_ID="client-id",
            GOOGLE_OAUTH_CLIENT_SECRET="client-secret",
            GOOGLE_OAUTH_REDIRECT_URI="http://127.0.0.1:8000/api/connections/gmail/callback",
            GMAIL_TOKEN_ENCRYPTION_KEY="not-a-fernet-key",
        )


def test_production_gmail_requires_https_frontend_origins():
    with pytest.raises(ValidationError, match="CORS_ORIGINS must use HTTPS"):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            SECRET_KEY="unit-test-production-secret-key-0123456789abcdef",
            GMAIL_INTEGRATION_ENABLED=True,
            GOOGLE_OAUTH_CLIENT_ID="client-id",
            GOOGLE_OAUTH_CLIENT_SECRET="client-secret",
            GOOGLE_OAUTH_REDIRECT_URI="https://api.example.test/api/connections/gmail/callback",
            CORS_ORIGINS=["https://app.example.test", "http://localhost:5173"],
            GMAIL_TOKEN_ENCRYPTION_KEY=Fernet.generate_key().decode("ascii"),
        )


def test_non_development_rejects_default_or_short_jwt_secret():
    with pytest.raises(ValidationError, match="SECRET_KEY must be replaced"):
        Settings(_env_file=None, ENVIRONMENT="production")


def test_production_accepts_explicit_strong_jwt_secret():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        SECRET_KEY="unit-test-production-secret-key-0123456789abcdef",
    )
    assert settings.ENVIRONMENT == "production"


def test_gmail_frontend_origin_rejects_path_or_credentials():
    with pytest.raises(ValidationError, match="valid frontend origins"):
        Settings(
            _env_file=None,
            GMAIL_INTEGRATION_ENABLED=True,
            GOOGLE_OAUTH_CLIENT_ID="client-id",
            GOOGLE_OAUTH_CLIENT_SECRET="client-secret",
            GOOGLE_OAUTH_REDIRECT_URI="http://127.0.0.1:8000/api/connections/gmail/callback",
            CORS_ORIGINS=["http://localhost:5173/untrusted-path"],
            GMAIL_TOKEN_ENCRYPTION_KEY=Fernet.generate_key().decode("ascii"),
        )
