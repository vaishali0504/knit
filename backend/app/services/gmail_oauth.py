from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from urllib.parse import urlencode

import httpx
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.connected_account import ConnectedAccount
from app.models.email import Email
from app.models.oauth_state import OAuthState
from app.schemas.connection import ConnectedAccountResponse
from app.services.token_encryption import decrypt_token, encrypt_token


STATE_TTL = timedelta(minutes=10)
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


class GmailOAuthError(Exception):
    """Safe error for Gmail OAuth flow failures."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _state_hash(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def start_authorization(db: Session, user_id: int) -> str:
    if not settings.GMAIL_INTEGRATION_ENABLED:
        raise GmailOAuthError("Gmail integration is not enabled")
    now = _utcnow()
    db.query(OAuthState).filter(or_(
        OAuthState.expires_at <= now,
        OAuthState.consumed_at.is_not(None),
    )).delete(synchronize_session=False)
    state = secrets.token_urlsafe(32)
    db.add(OAuthState(state_hash=_state_hash(state), user_id=user_id, expires_at=now + STATE_TTL))
    db.commit()
    query = urlencode({
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(settings.GMAIL_OAUTH_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    })
    return f"{GOOGLE_AUTH_URL}?{query}"


def consume_state(db: Session, state: str) -> int:
    if not state or len(state) > 512:
        raise GmailOAuthError("OAuth state is invalid or expired")
    hashed = _state_hash(state)
    row = db.query(OAuthState).filter(OAuthState.state_hash == hashed).first()
    now = _utcnow()
    if row is None or row.consumed_at is not None:
        raise GmailOAuthError("OAuth state is invalid or expired")
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        row.consumed_at = now
        db.commit()
        raise GmailOAuthError("OAuth state is invalid or expired")
    # Conditional update makes state single-use even when two callbacks race.
    changed = db.query(OAuthState).filter(
        OAuthState.id == row.id,
        OAuthState.consumed_at.is_(None),
        OAuthState.expires_at > now,
    ).update({OAuthState.consumed_at: now}, synchronize_session=False)
    db.commit()
    if changed != 1:
        raise GmailOAuthError("OAuth state is invalid or expired")
    return row.user_id


def complete_authorization(db: Session, state: str, code: str) -> None:
    if not settings.GMAIL_INTEGRATION_ENABLED:
        raise GmailOAuthError("Gmail integration is not enabled")
    user_id = consume_state(db, state)
    if not code or len(code) > 4096:
        raise GmailOAuthError("Google authorization was not completed")
    try:
        token_response = httpx.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "grant_type": "authorization_code",
        }, timeout=15)
        token_response.raise_for_status()
        token_data = token_response.json()
        access_token = token_data["access_token"]
        granted_scopes = str(token_data.get("scope", "")).split()
        if not access_token or READONLY_SCOPE not in granted_scopes or set(granted_scopes) - {READONLY_SCOPE}:
            raise GmailOAuthError("Google did not grant the required read-only permission")
        profile_response = httpx.get(
            GMAIL_PROFILE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        profile_response.raise_for_status()
        profile = profile_response.json()
        email_address = profile.get("emailAddress")
        if not isinstance(email_address, str) or "@" not in email_address:
            raise GmailOAuthError("Google account identity could not be verified")
        account_id = email_address.strip().lower()
        existing = db.query(ConnectedAccount).filter_by(
            user_id=user_id, provider="gmail", provider_account_id=account_id,
        ).first()
        refresh_token = token_data.get("refresh_token")
        if not refresh_token and existing:
            refresh_token = decrypt_token(existing.encrypted_refresh_token)
        if not refresh_token:
            raise GmailOAuthError("Google did not provide a refresh token; reconnect with consent")
        expires_in = int(token_data.get("expires_in", 3600))
        if expires_in <= 0 or expires_in > 86400:
            raise GmailOAuthError("Google returned an invalid token lifetime")
        encrypted_access = encrypt_token(access_token)
        encrypted_refresh = encrypt_token(refresh_token)
        if existing:
            existing.email_address = email_address
            existing.encrypted_access_token = encrypted_access
            existing.encrypted_refresh_token = encrypted_refresh
            existing.token_expires_at = _utcnow() + timedelta(seconds=expires_in)
            existing.granted_scopes = granted_scopes
            existing.sync_status = "pending"
            existing.sync_error_code = None
            existing.sync_error_message = None
        else:
            db.add(ConnectedAccount(
                user_id=user_id,
                provider="gmail",
                provider_account_id=account_id,
                email_address=email_address,
                encrypted_access_token=encrypted_access,
                encrypted_refresh_token=encrypted_refresh,
                token_expires_at=_utcnow() + timedelta(seconds=expires_in),
                granted_scopes=granted_scopes,
                sync_status="pending",
            ))
        db.commit()
    except GmailOAuthError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        # Deliberately discard provider exception details; they can contain sensitive data.
        raise GmailOAuthError("Google authorization could not be completed") from None


def list_accounts(db: Session, user_id: int) -> list[ConnectedAccountResponse]:
    rows = db.query(ConnectedAccount).filter_by(user_id=user_id, provider="gmail").order_by(ConnectedAccount.id).all()
    return [ConnectedAccountResponse(
        id=row.id,
        provider="gmail",
        email_address=row.email_address,
        status=row.sync_status,
        scopes=row.granted_scopes,
        last_successful_sync_at=row.last_successful_sync_at,
    ) for row in rows]


def disconnect(db: Session, user_id: int, account_id: int) -> bool:
    account = db.query(ConnectedAccount).filter_by(id=account_id, user_id=user_id, provider="gmail").first()
    if account is None:
        return False
    try:
        token = decrypt_token(account.encrypted_access_token)
        httpx.post(GOOGLE_REVOKE_URL, data={"token": token}, timeout=10)
    except Exception:
        # Local credential deletion is authoritative even if remote revocation is unavailable.
        pass
    db.query(Email).filter(Email.connected_account_id == account.id).update(
        {Email.connected_account_id: None}, synchronize_session=False,
    )
    db.delete(account)
    db.commit()
    return True
