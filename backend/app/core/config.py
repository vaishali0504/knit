from typing import List
from urllib.parse import urlparse
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet


class Settings(BaseSettings):
    """KNIT Application Settings."""

    APP_NAME: str = "KNIT"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Prefix
    API_V1_PREFIX: str = "/api"

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ],
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "CORS_ORIGINS"),
    )
    FRONTEND_URL: str = ""

    # Database Configuration (SQLite for local MVP)
    DATABASE_URL: str = "sqlite:///./knit.db"

    # JWT Authentication Settings
    SECRET_KEY: str = Field(
        default="knit-super-secure-jwt-secret-key-phase3-2026-production-ready",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY"),
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 7,
        validation_alias=AliasChoices("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "ACCESS_TOKEN_EXPIRE_MINUTES"),
    )

    # Gemini AI configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_TIMEOUT_SECONDS: int = 60

    # Gmail OAuth configuration. Credentials remain backend-only.
    GMAIL_INTEGRATION_ENABLED: bool = False
    GOOGLE_OAUTH_CLIENT_ID: str = Field(
        default="",
        validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_ID"),
    )
    GOOGLE_OAUTH_CLIENT_SECRET: str = Field(
        default="",
        validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "GOOGLE_OAUTH_CLIENT_SECRET"),
    )
    GOOGLE_OAUTH_REDIRECT_URI: str = Field(
        default="http://127.0.0.1:8000/api/connections/gmail/callback",
        validation_alias=AliasChoices("GMAIL_REDIRECT_URI", "GOOGLE_OAUTH_REDIRECT_URI"),
    )
    GMAIL_OAUTH_SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.readonly"]
    GMAIL_TOKEN_ENCRYPTION_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("TOKEN_ENCRYPTION_KEY", "GMAIL_TOKEN_ENCRYPTION_KEY"),
    )
    GMAIL_SYNC_MAX_MESSAGES: int = Field(default=100, ge=1, le=500)
    GMAIL_SYNC_PAGE_SIZE: int = Field(default=25, ge=1, le=100)

    @model_validator(mode="after")
    def validate_gmail_configuration(self):
        if self.ENVIRONMENT != "development":
            if (
                self.SECRET_KEY == "knit-super-secure-jwt-secret-key-phase3-2026-production-ready"
                or len(self.SECRET_KEY) < 32
            ):
                raise ValueError("SECRET_KEY must be replaced with a strong key outside development")
        if self.FRONTEND_URL:
            frontend = urlparse(self.FRONTEND_URL)
            if (
                frontend.scheme not in ("http", "https")
                or not frontend.netloc
                or frontend.username
                or frontend.password
                or frontend.path not in ("", "/")
                or frontend.query
                or frontend.fragment
            ):
                raise ValueError("FRONTEND_URL must be an absolute HTTP(S) origin without a path or credentials")
            if self.ENVIRONMENT != "development" and frontend.scheme != "https":
                raise ValueError("FRONTEND_URL must use HTTPS outside development")
            frontend_origin = self.FRONTEND_URL.rstrip("/")
            if frontend_origin not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append(frontend_origin)
        if not self.GMAIL_INTEGRATION_ENABLED:
            return self

        required = {
            "GOOGLE_OAUTH_CLIENT_ID": self.GOOGLE_OAUTH_CLIENT_ID,
            "GOOGLE_OAUTH_CLIENT_SECRET": self.GOOGLE_OAUTH_CLIENT_SECRET,
            "GOOGLE_OAUTH_REDIRECT_URI": self.GOOGLE_OAUTH_REDIRECT_URI,
            "GMAIL_TOKEN_ENCRYPTION_KEY": self.GMAIL_TOKEN_ENCRYPTION_KEY,
        }
        missing = [name for name, value in required.items() if not value.strip()]
        if missing:
            raise ValueError(
                "Gmail integration is enabled but required configuration is missing: "
                + ", ".join(missing)
            )
        try:
            Fernet(self.GMAIL_TOKEN_ENCRYPTION_KEY.encode("ascii"))
        except (ValueError, UnicodeEncodeError, TypeError):
            raise ValueError("GMAIL_TOKEN_ENCRYPTION_KEY must be a valid Fernet key") from None
        expected_scope = "https://www.googleapis.com/auth/gmail.readonly"
        if self.GMAIL_OAUTH_SCOPES != [expected_scope]:
            raise ValueError("GMAIL_OAUTH_SCOPES must contain only the Gmail read-only scope")
        redirect = urlparse(self.GOOGLE_OAUTH_REDIRECT_URI)
        if redirect.scheme not in ("http", "https") or not redirect.netloc:
            raise ValueError("Google OAuth redirect URI must be a valid absolute HTTP(S) URL")
        if redirect.scheme != "https" and self.ENVIRONMENT != "development":
            raise ValueError("Google OAuth redirect URI must use HTTPS outside development")
        if not self.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS must include the trusted frontend origin for Gmail OAuth")
        for origin in self.CORS_ORIGINS:
            parsed_origin = urlparse(origin)
            if (
                parsed_origin.scheme not in ("http", "https")
                or not parsed_origin.netloc
                or parsed_origin.username
                or parsed_origin.password
                or parsed_origin.path not in ("", "/")
                or parsed_origin.query
                or parsed_origin.fragment
            ):
                raise ValueError("CORS_ORIGINS must contain valid frontend origins without paths or credentials")
            if self.ENVIRONMENT != "development" and parsed_origin.scheme != "https":
                raise ValueError("CORS_ORIGINS must use HTTPS outside development")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
