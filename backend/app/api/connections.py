from pathlib import Path
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.connection import (
    ConnectedAccountsResponse,
    GmailAuthorizeResponse,
    GmailSyncSettingsUpdate,
)
from app.schemas.sync import SyncResponse
from app.services import gmail_oauth
from app.services.email_sync import SyncError, sync_gmail_account


router = APIRouter()


def _settings_redirect(result: str) -> str:
    # Only configured frontend origins are used; callback inputs never select a URL.
    frontend_origin = settings.FRONTEND_URL.rstrip("/") or (
        settings.CORS_ORIGINS[0].rstrip("/") if settings.CORS_ORIGINS else "http://localhost:5173"
    )
    return f"{frontend_origin}/app/settings?gmail={result}"


def _callback_redirect(result: str) -> RedirectResponse:
    response = RedirectResponse(_settings_redirect(result), status_code=302)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@router.post("/gmail/authorize", response_model=GmailAuthorizeResponse)
def authorize_gmail(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return GmailAuthorizeResponse(authorization_url=gmail_oauth.start_authorization(db, current_user.id))
    except gmail_oauth.GmailOAuthError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/gmail/callback")
def gmail_callback(
    state: str | None = Query(default=None),
    code: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        if error:
            gmail_oauth.consume_state(db, state or "")
            return _callback_redirect("denied")
        gmail_oauth.complete_authorization(db, state or "", code or "")
        return _callback_redirect("connected")
    except gmail_oauth.GmailOAuthError:
        return _callback_redirect("error")


@router.get("", response_model=ConnectedAccountsResponse)
def get_connections(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ConnectedAccountsResponse(items=gmail_oauth.list_accounts(db, current_user.id))


@router.get("/status")
def get_connection_status(current_user: User = Depends(get_current_user)):
    credentials_configured = bool(
        settings.GOOGLE_OAUTH_CLIENT_ID
        and settings.GOOGLE_OAUTH_CLIENT_SECRET
        and settings.GMAIL_TOKEN_ENCRYPTION_KEY
    )
    return {
        "enabled": settings.GMAIL_INTEGRATION_ENABLED,
        "credentials_configured": credentials_configured,
        "sync_max_messages": settings.GMAIL_SYNC_MAX_MESSAGES,
        "sync_page_size": settings.GMAIL_SYNC_PAGE_SIZE,
    }


@router.patch("/status")
def update_connection_status(
    update: GmailSyncSettingsUpdate,
    current_user: User = Depends(get_current_user),
):
    if update.sync_page_size > update.sync_max_messages:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sync page size cannot exceed the maximum messages per sync.",
        )
    settings.GMAIL_SYNC_MAX_MESSAGES = update.sync_max_messages
    settings.GMAIL_SYNC_PAGE_SIZE = update.sync_page_size
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8")
        env_text = re.sub(
            r"^GMAIL_SYNC_MAX_MESSAGES=.*$",
            f"GMAIL_SYNC_MAX_MESSAGES={update.sync_max_messages}",
            env_text,
            flags=re.MULTILINE,
        )
        env_text = re.sub(
            r"^GMAIL_SYNC_PAGE_SIZE=.*$",
            f"GMAIL_SYNC_PAGE_SIZE={update.sync_page_size}",
            env_text,
            flags=re.MULTILINE,
        )
        env_path.write_text(env_text, encoding="utf-8")
    return get_connection_status(current_user)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not gmail_oauth.disconnect(db, current_user.id, account_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connected account not found")
    return None


@router.post("/{account_id}/sync", response_model=SyncResponse)
def sync_connection(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return sync_gmail_account(db, current_user.id, account_id)
    except SyncError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
