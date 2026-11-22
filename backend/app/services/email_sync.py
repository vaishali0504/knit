from datetime import datetime, timedelta, timezone
import secrets

import httpx
from sqlalchemy import or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.connected_account import ConnectedAccount
from app.models.email import Email
from app.providers import GmailProvider, GmailProviderError, ProviderPage
from app.schemas.sync import SyncResponse
from app.services.gmail_normalizer import normalize_gmail_message
from app.services.token_encryption import TokenEncryptionError, decrypt_token, encrypt_token


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
REQUIRED_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
SYNC_LEASE = timedelta(minutes=15)


class SyncError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 502):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _safe_message(code: str) -> str:
    return {
        "reauthorization_required": "Reconnect this Gmail account to continue syncing.",
        "permission_denied": "Gmail denied the requested read-only access.",
        "rate_limited": "Gmail temporarily limited requests. Try syncing again later.",
        "provider_timeout": "Gmail did not respond in time. Try syncing again.",
        "provider_unavailable": "Gmail is temporarily unavailable. Try syncing again.",
        "provider_request_failed": "Gmail could not complete the sync request.",
        "invalid_provider_response": "Gmail returned an unsupported response.",
        "history_cursor_invalid": "Gmail history expired. Run a full resynchronization to continue.",
        "account_identity_mismatch": "The authorized Gmail account does not match this connection.",
        "invalid_token_configuration": "Gmail token configuration is unavailable.",
    }.get(code, "Gmail sync could not be completed.")


def _claim_sync(db: Session, account: ConnectedAccount) -> str | None:
    now = _now()
    lease_token = secrets.token_urlsafe(32)
    stale_before = now - SYNC_LEASE
    result = db.execute(update(ConnectedAccount).where(
        ConnectedAccount.id == account.id,
        ConnectedAccount.user_id == account.user_id,
        or_(ConnectedAccount.sync_status != "syncing", ConnectedAccount.sync_started_at.is_(None), ConnectedAccount.sync_started_at < stale_before),
    ).values(
        sync_status="syncing",
        sync_started_at=now,
        sync_lease_token=lease_token,
        sync_error_code=None,
        sync_error_message=None,
    ).execution_options(synchronize_session=False))
    db.commit()
    return lease_token if result.rowcount == 1 else None


def _heartbeat_sync(db: Session, account: ConnectedAccount, lease_token: str) -> None:
    now = _now()
    result = db.execute(update(ConnectedAccount).where(
        ConnectedAccount.id == account.id,
        ConnectedAccount.user_id == account.user_id,
        ConnectedAccount.sync_status == "syncing",
        ConnectedAccount.sync_lease_token == lease_token,
        ConnectedAccount.sync_started_at >= now - SYNC_LEASE,
    ).values(sync_started_at=now).execution_options(synchronize_session=False))
    db.commit()
    if result.rowcount != 1:
        raise SyncError("sync_lease_lost", "Sync lease ownership changed.", 409)


def _save_sync_progress(db: Session, account: ConnectedAccount, lease_token: str, **values) -> None:
    values["sync_started_at"] = _now()
    result = db.execute(update(ConnectedAccount).where(
        ConnectedAccount.id == account.id,
        ConnectedAccount.user_id == account.user_id,
        ConnectedAccount.sync_status == "syncing",
        ConnectedAccount.sync_lease_token == lease_token,
        ConnectedAccount.sync_started_at >= _now() - SYNC_LEASE,
    ).values(**values).execution_options(synchronize_session=False))
    db.commit()
    if result.rowcount != 1:
        raise SyncError("sync_lease_lost", "Sync lease ownership changed.", 409)
    db.refresh(account)


def _refresh_access_token(db: Session, account: ConnectedAccount, lease_token: str) -> str:
    now = _now()
    expires_at = _aware(account.token_expires_at)
    if expires_at and expires_at > now + timedelta(seconds=60):
        return decrypt_token(account.encrypted_access_token)
    refresh = decrypt_token(account.encrypted_refresh_token)
    try:
        response = httpx.post(GOOGLE_TOKEN_URL, data={
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "refresh_token": refresh,
            "grant_type": "refresh_token",
        }, timeout=15)
        status_code = response.status_code
        if status_code >= 400:
            if status_code == 429:
                raise SyncError("rate_limited", _safe_message("rate_limited"), 429)
            if status_code in (400, 401):
                raise SyncError("reauthorization_required", _safe_message("reauthorization_required"), 401)
            raise SyncError("provider_unavailable", _safe_message("provider_unavailable"), 502)
        payload = response.json()
        access_token = payload.get("access_token")
        expires_in = int(payload.get("expires_in", 3600))
        if not isinstance(access_token, str) or not access_token or expires_in <= 0 or expires_in > 86400:
            raise SyncError("invalid_provider_response", _safe_message("invalid_provider_response"))
        values = {
            "encrypted_access_token": encrypt_token(access_token),
            "token_expires_at": now + timedelta(seconds=expires_in),
        }
        rotated_refresh = payload.get("refresh_token")
        if isinstance(rotated_refresh, str) and rotated_refresh:
            values["encrypted_refresh_token"] = encrypt_token(rotated_refresh)
        _save_sync_progress(db, account, lease_token, **values)
        return access_token
    except SyncError:
        raise
    except httpx.TimeoutException:
        raise SyncError("provider_timeout", _safe_message("provider_timeout")) from None
    except httpx.HTTPError:
        raise SyncError("provider_unavailable", _safe_message("provider_unavailable")) from None
    except (ValueError, TypeError, TokenEncryptionError):
        raise SyncError("invalid_token_configuration", _safe_message("invalid_token_configuration"), 503) from None


def _finish(db: Session, account: ConnectedAccount, lease_token: str, status: str, code: str | None = None) -> bool:
    values = {
        "sync_status": status,
        "sync_started_at": None,
        "sync_lease_token": None,
        "sync_error_code": code,
        "sync_error_message": _safe_message(code) if code else None,
    }
    if status == "complete":
        values["last_successful_sync_at"] = _now()
    result = db.execute(update(ConnectedAccount).where(
        ConnectedAccount.id == account.id,
        ConnectedAccount.user_id == account.user_id,
        ConnectedAccount.sync_status == "syncing",
        ConnectedAccount.sync_lease_token == lease_token,
    ).values(**values).execution_options(synchronize_session=False))
    db.commit()
    if result.rowcount != 1:
        return False
    db.refresh(account)
    return True


def _finish_or_raise(db: Session, account: ConnectedAccount, lease_token: str, status: str, code: str | None = None) -> None:
    if not _finish(db, account, lease_token, status, code):
        raise SyncError("sync_lease_lost", "Sync lease ownership changed.", 409)


def _response(account: ConnectedAccount, sync_type: str, status: str, added=0, updated=0, removed=0, skipped=0, failed=0, limit_reached=False, error_code=None, message=None) -> SyncResponse:
    return SyncResponse(
        sync_type=sync_type,
        status=status,
        added=added,
        updated=updated,
        removed=removed,
        last_successful_sync_at=account.last_successful_sync_at,
        imported=added,
        skipped=skipped,
        failed=failed,
        limit_reached=limit_reached,
        error_code=error_code,
        message=message,
    )


def _set_user_owned_fields(existing: Email, values: dict) -> bool:
    # Provider refreshes must never overwrite an explicit KNIT user choice.
    changed = False
    for name in ("sender_name", "sender_email", "recipient", "subject", "body", "received_at", "attachments", "provider_thread_id"):
        if getattr(existing, name) != values[name]:
            setattr(existing, name, values[name])
            changed = True
    if not existing.is_read_user_modified:
        if existing.is_read != values["is_read"]:
            existing.is_read = values["is_read"]
            changed = True
    if not existing.is_important_user_modified:
        if existing.is_important != values["is_important"]:
            existing.is_important = values["is_important"]
            changed = True
    return changed


def _record_message(db: Session, account: ConnectedAccount, user_id: int, provider: GmailProvider, message_id: str, seen_at: datetime, lease_token: str) -> tuple[str, Email]:
    message = provider.get_message(message_id)
    _heartbeat_sync(db, account, lease_token)
    values = normalize_gmail_message(message, user_id, account.id)
    existing = db.query(Email).filter_by(connected_account_id=account.id, provider_message_id=message_id).first()
    if existing:
        changed = _set_user_owned_fields(existing, values)
        existing.provider_sync_seen_at = seen_at
        db.commit()
        db.refresh(existing)
        return ("updated" if changed else "skipped"), existing
    values["provider_sync_seen_at"] = seen_at
    email = Email(**values)
    db.add(email)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(Email).filter_by(connected_account_id=account.id, provider_message_id=message_id).first()
        if existing:
            _set_user_owned_fields(existing, values)
            existing.provider_sync_seen_at = seen_at
            db.commit()
            return "updated", existing
        raise
    return "added", email


def _start_initial(db: Session, account: ConnectedAccount, provider: GmailProvider, full_resync: bool, lease_token: str) -> None:
    values = {
        "gmail_sync_baseline_history_id": provider.current_history_id(),
        "gmail_sync_page_token": None,
    }
    if full_resync:
        values["full_resync_started_at"] = _now()
    _save_sync_progress(db, account, lease_token, **values)


def _run_initial(db: Session, account: ConnectedAccount, provider: GmailProvider, user_id: int, max_messages: int, page_size: int, full_resync: bool, totals: dict, lease_token: str) -> tuple[bool, bool]:
    if not account.gmail_sync_baseline_history_id:
        _start_initial(db, account, provider, full_resync, lease_token)
    seen_at = _aware(account.full_resync_started_at) or _now()
    processed = 0
    page_token = account.gmail_sync_page_token
    seen_tokens: set[str] = set()
    complete = False
    max_pages = max(1, (max_messages + page_size - 1) // page_size)
    pages_processed = 0
    while processed < max_messages and pages_processed < max_pages:
        page: ProviderPage = provider.list_messages(page_token, min(page_size, max_messages - processed))
        pages_processed += 1
        _heartbeat_sync(db, account, lease_token)
        for stub in page.messages[:max_messages - processed]:
            processed += 1
            message_id = stub.get("id")
            if not isinstance(message_id, str) or not message_id:
                totals["failed"] += 1
                continue
            try:
                action, email = _record_message(db, account, user_id, provider, message_id, seen_at, lease_token)
                totals[action] += 1
                _heartbeat_sync(db, account, lease_token)
            except GmailProviderError as exc:
                db.rollback()
                if exc.code == "message_not_found":
                    totals["skipped"] += 1
                    _heartbeat_sync(db, account, lease_token)
                    continue
                raise
            except ValueError:
                db.rollback()
                totals["failed"] += 1
        next_page_token = page.next_page_token
        if totals["failed"]:
            # Do not establish a baseline cursor if any message on this page
            # could not be processed; retain the prior page token so a later
            # sync retries this page rather than skipping failed messages.
            return False, bool(next_page_token)
        page_token = next_page_token
        _save_sync_progress(db, account, lease_token, gmail_sync_page_token=page_token)
        if not page_token:
            complete = True
            break
        if page_token in seen_tokens:
            raise GmailProviderError("invalid_provider_response")
        seen_tokens.add(page_token)
    return complete, bool(page_token) and (processed >= max_messages or pages_processed >= max_pages)


def _apply_history_page(db: Session, account: ConnectedAccount, provider: GmailProvider, user_id: int, history: list[dict], seen_at: datetime, totals: dict, remaining: int, lease_token: str) -> int:
    updates: set[str] = set()
    removals: set[str] = set()
    for entry in history:
        for item in entry.get("messagesDeleted", []) or []:
            message = item.get("message", {}) if isinstance(item, dict) else {}
            message_id = message.get("id")
            if message_id:
                removals.add(str(message_id))
        for item in entry.get("labelsAdded", []) or []:
            if not isinstance(item, dict):
                continue
            message = item.get("message", {})
            if "TRASH" in (item.get("labelIds") or []):
                message_id = message.get("id")
                if message_id:
                    removals.add(str(message_id))
        for key in ("messagesAdded", "labelsAdded", "labelsRemoved"):
            for item in entry.get(key, []) or []:
                message = item.get("message", {}) if isinstance(item, dict) else {}
                message_id = message.get("id")
                if message_id and str(message_id) not in removals:
                    updates.add(str(message_id))

    updates -= removals
    if len(updates) + len(removals) > remaining:
        raise SyncError("sync_limit_reached", "History changes exceed the per-run processing limit.", 429)

    for message_id in sorted(removals):
        email = db.query(Email).filter_by(connected_account_id=account.id, provider_message_id=message_id).first()
        if email and not email.is_deleted_user_modified and not email.is_deleted:
            email.is_deleted = True
            email.deleted_at = _now()
            email.provider_sync_seen_at = seen_at
            totals["removed"] += 1
        elif email:
            email.provider_sync_seen_at = seen_at
        db.commit()
        _heartbeat_sync(db, account, lease_token)
        remaining -= 1
    for message_id in sorted(updates):
        try:
            action, _ = _record_message(db, account, user_id, provider, message_id, seen_at, lease_token)
            totals[action] += 1
            _heartbeat_sync(db, account, lease_token)
        except GmailProviderError as exc:
            db.rollback()
            if exc.code != "message_not_found":
                raise
            # A message can disappear between its history event and detail
            # fetch. Gmail's history stream remains authoritative for the
            # removal event, so this missing detail is a safe no-op.
            totals["skipped"] += 1
            _heartbeat_sync(db, account, lease_token)
        remaining -= 1
    return remaining


def _run_incremental(db: Session, account: ConnectedAccount, provider: GmailProvider, user_id: int, max_messages: int, page_size: int, totals: dict, lease_token: str) -> bool:
    if account.gmail_sync_baseline_history_id:
        start_history_id = account.gmail_sync_baseline_history_id
        page_token = account.gmail_sync_page_token
    else:
        start_history_id = account.gmail_history_id
        page_token = None
        _save_sync_progress(db, account, lease_token,
                            gmail_sync_baseline_history_id=start_history_id,
                            gmail_sync_page_token=None)
    remaining = max_messages
    seen_tokens: set[str] = set()
    final_history_id: str | None = None
    max_pages = max(1, (max_messages + page_size - 1) // page_size)
    pages_processed = 0
    while True:
        if pages_processed >= max_pages:
            return False
        page = provider.list_history(start_history_id, page_token, min(page_size, max(remaining, 1)))
        pages_processed += 1
        _heartbeat_sync(db, account, lease_token)
        if page.history_id:
            final_history_id = page.history_id
        remaining = _apply_history_page(db, account, provider, user_id, page.history, _now(), totals, remaining, lease_token)
        page_token = page.next_page_token
        _save_sync_progress(db, account, lease_token, gmail_sync_page_token=page_token)
        if not page_token:
            break
        if page_token in seen_tokens:
            raise GmailProviderError("invalid_provider_response")
        seen_tokens.add(page_token)
        if remaining <= 0:
            return False
    if not final_history_id:
        raise GmailProviderError("invalid_provider_response")
    _save_sync_progress(db, account, lease_token,
                        gmail_history_id=final_history_id,
                        gmail_sync_baseline_history_id=None,
                        gmail_sync_page_token=None)
    return True


def _complete_full_resync(db: Session, account: ConnectedAccount, lease_token: str) -> None:
    started_at = _aware(account.full_resync_started_at)
    if started_at:
        last_id = 0
        while True:
            stale = db.query(Email).filter(
                Email.connected_account_id == account.id,
                Email.id > last_id,
                Email.provider_sync_seen_at.is_(None) | (Email.provider_sync_seen_at < started_at),
                Email.is_deleted_user_modified.is_(False),
                Email.is_deleted.is_(False),
            ).order_by(Email.id).limit(100).all()
            if not stale:
                break
            for email in stale:
                email.is_deleted = True
                email.deleted_at = _now()
            last_id = stale[-1].id
            db.commit()
            _heartbeat_sync(db, account, lease_token)
    _save_sync_progress(db, account, lease_token, full_resync_started_at=None)


def sync_gmail_account(db: Session, user_id: int, account_id: int) -> SyncResponse:
    if not settings.GMAIL_INTEGRATION_ENABLED:
        raise SyncError("integration_disabled", "Gmail integration is not enabled.", 503)
    account = db.query(ConnectedAccount).filter_by(id=account_id, user_id=user_id, provider="gmail").first()
    if account is None:
        raise SyncError("not_found", "Connected account not found.", 404)
    if account.granted_scopes != [REQUIRED_SCOPE]:
        raise SyncError("permission_denied", _safe_message("permission_denied"), 403)
    prior_status = account.sync_status
    lease_token = _claim_sync(db, account)
    if lease_token is None:
        raise SyncError("sync_in_progress", "A sync is already running for this account.", 409)
    account = db.query(ConnectedAccount).filter_by(id=account_id, user_id=user_id, sync_lease_token=lease_token).one()
    totals = {"added": 0, "updated": 0, "removed": 0, "skipped": 0, "failed": 0}
    sync_type = "incremental" if account.gmail_history_id else "initial"
    full_resync = prior_status == "full_resync_required" or account.full_resync_started_at is not None
    if account.gmail_sync_baseline_history_id:
        sync_type = "incremental" if account.gmail_history_id else "initial"
    try:
        access_token = _refresh_access_token(db, account, lease_token)
        provider = GmailProvider(access_token)
        if provider.account_identity() != account.provider_account_id.lower():
            raise SyncError("account_identity_mismatch", _safe_message("account_identity_mismatch"), 403)

        max_messages = settings.GMAIL_SYNC_MAX_MESSAGES
        page_size = min(settings.GMAIL_SYNC_PAGE_SIZE, max_messages)
        if account.gmail_history_id and not full_resync:
            sync_type = "incremental"
            complete = _run_incremental(db, account, provider, user_id, max_messages, page_size, totals, lease_token)
        else:
            sync_type = "initial"
            if full_resync and account.full_resync_started_at is None:
                _save_sync_progress(db, account, lease_token,
                                    gmail_history_id=None,
                                    gmail_sync_baseline_history_id=None,
                                    gmail_sync_page_token=None,
                                    full_resync_started_at=_now())
            complete, limit_reached = _run_initial(db, account, provider, user_id, max_messages, page_size, full_resync, totals, lease_token)
            if not complete:
                pending_status = "full_resync_required" if full_resync else "initial_sync_pending"
                _finish_or_raise(db, account, lease_token, pending_status)
                return _response(account, sync_type, pending_status, **totals, limit_reached=limit_reached)
            _save_sync_progress(db, account, lease_token,
                                gmail_history_id=account.gmail_sync_baseline_history_id,
                                gmail_sync_baseline_history_id=None,
                                gmail_sync_page_token=None)
            if full_resync:
                _complete_full_resync(db, account, lease_token)

        if not complete:
            _finish_or_raise(db, account, lease_token, "incremental_sync_pending")
            return _response(account, sync_type, "incremental_sync_pending", **totals, limit_reached=True)
        _finish_or_raise(db, account, lease_token, "complete", "provider_request_failed" if totals["failed"] else None)
        return _response(account, sync_type, "complete", **totals, limit_reached=False)
    except GmailProviderError as exc:
        db.rollback()
        account = db.query(ConnectedAccount).filter_by(id=account_id, user_id=user_id, sync_lease_token=lease_token).first()
        if not account:
            raise SyncError("sync_in_progress", "A sync is already running for this account.", 409) from None
        if exc.code == "history_cursor_invalid" and account.gmail_history_id:
            _save_sync_progress(db, account, lease_token,
                                gmail_history_id=None,
                                gmail_sync_baseline_history_id=None,
                                gmail_sync_page_token=None,
                                full_resync_started_at=None)
            _finish_or_raise(db, account, lease_token, "full_resync_required", exc.code)
        else:
            _finish_or_raise(db, account, lease_token, "partial" if totals["added"] or totals["updated"] or totals["removed"] else "error", exc.code)
        response_totals = {**totals, "failed": max(totals["failed"], 1)}
        return _response(account, sync_type, account.sync_status, **response_totals, error_code=exc.code, message=_safe_message(exc.code))
    except SyncError as exc:
        if exc.code == "sync_lease_lost":
            # Do not clear a lease that now belongs to another worker.
            raise SyncError("sync_in_progress", "A sync is already running for this account.", 409) from None
        db.rollback()
        account = db.query(ConnectedAccount).filter_by(id=account_id, user_id=user_id, sync_lease_token=lease_token).first()
        if account:
            status = "partial" if totals["added"] or totals["updated"] or totals["removed"] else "error"
            if exc.code == "sync_limit_reached":
                status = "incremental_sync_pending"
            _finish_or_raise(db, account, lease_token, status, exc.code)
            response_totals = {**totals, "failed": max(totals["failed"], 1)}
            return _response(account, sync_type, status, **response_totals, limit_reached=exc.code == "sync_limit_reached", error_code=exc.code, message=exc.message)
        raise SyncError("sync_in_progress", "A sync is already running for this account.", 409) from None
    except TokenEncryptionError:
        db.rollback()
        account = db.query(ConnectedAccount).filter_by(id=account_id, user_id=user_id, sync_lease_token=lease_token).first()
        if account:
            _finish_or_raise(db, account, lease_token, "error", "invalid_token_configuration")
            return _response(account, sync_type, "error", **{**totals, "failed": 1}, error_code="invalid_token_configuration", message=_safe_message("invalid_token_configuration"))
        raise SyncError("sync_in_progress", "A sync is already running for this account.", 409) from None
    except Exception:
        db.rollback()
        account = db.query(ConnectedAccount).filter_by(id=account_id, user_id=user_id, sync_lease_token=lease_token).first()
        if account:
            status = "partial" if totals["added"] or totals["updated"] or totals["removed"] else "error"
            _finish_or_raise(db, account, lease_token, status, "provider_request_failed")
            response_totals = {**totals, "failed": max(totals["failed"], 1)}
            return _response(account, sync_type, status, **response_totals, error_code="provider_request_failed", message=_safe_message("provider_request_failed"))
        raise SyncError("sync_in_progress", "A sync is already running for this account.", 409) from None
