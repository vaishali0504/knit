from math import ceil
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.user import User
from app.repositories import email as email_repo
from app.schemas.email import EmailCounts, EmailListItem, EmailListResponse
VALID_CATEGORIES = {
    "all",
    "internship",
    "interview",
    "college",
    "important",
    "personal",
    "promotions",
    "updates",
    "suspicious",
    "other",
}


def ensure_sample_emails(db: Session, user: User) -> None:
    """Demo seeding is disabled; Gmail and explicitly imported mail are authoritative."""
    return None


def list_emails(
    db: Session,
    user: User,
    category: Optional[str],
    status_filter: Optional[str],
    search: Optional[str],
    sort: str,
    page: int,
    page_size: int,
    deleted: bool,
) -> EmailListResponse:
    ensure_sample_emails(db, user)
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=422, detail="Invalid email category.")
    if status_filter and status_filter not in {"read", "unread"}:
        raise HTTPException(status_code=422, detail="Status must be read or unread.")
    if sort not in {"newest", "oldest"}:
        raise HTTPException(status_code=422, detail="Sort must be newest or oldest.")

    items, total = email_repo.list_emails(
        db,
        user.id,
        category=None if category in (None, "all") else category,
        status=status_filter,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
        deleted=deleted,
    )
    list_items = [
        EmailListItem(
            id=item.id,
            sender_name=item.sender_name,
            sender_email=item.sender_email,
            subject=item.subject,
            preview=(item.body[:180].replace("\n", " ") + ("…" if len(item.body) > 180 else "")),
            received_at=item.received_at,
            category=item.category,
            is_read=item.is_read,
            is_important=item.is_important,
            is_deleted=item.is_deleted,
            deleted_at=item.deleted_at,
            attachment_count=len(item.attachments or []),
        )
        for item in items
    ]
    return EmailListResponse(
        items=list_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, ceil(total / page_size)),
    )


def get_email(db: Session, user: User, email_id: int) -> Email:
    ensure_sample_emails(db, user)
    email = email_repo.get_owned(db, user.id, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
    if not email.is_read:
        email_repo.set_read(db, email, True)
    return email


def set_read_status(db: Session, user: User, email_id: int, is_read: bool) -> Email:
    ensure_sample_emails(db, user)
    email = email_repo.get_owned(db, user.id, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
    return email_repo.set_read(db, email, is_read)


def set_important_status(db: Session, user: User, email_id: int, is_important: bool) -> Email:
    ensure_sample_emails(db, user)
    email = email_repo.get_owned(db, user.id, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
    return email_repo.set_important(db, email, is_important)


def soft_delete(db: Session, user: User, email_id: int) -> Email:
    ensure_sample_emails(db, user)
    email = email_repo.get_owned(db, user.id, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
    return email_repo.soft_delete(db, email)


def restore(db: Session, user: User, email_id: int) -> Email:
    ensure_sample_emails(db, user)
    email = email_repo.get_owned(db, user.id, email_id, include_deleted=True)
    if not email or not email.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deleted email not found.")
    return email_repo.restore(db, email)


def permanent_delete(db: Session, user: User, email_id: int) -> None:
    ensure_sample_emails(db, user)
    email = email_repo.get_owned(db, user.id, email_id, include_deleted=True)
    if not email or not email.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only deleted emails can be permanently deleted.")
    email_repo.permanent_delete(db, email)


def get_counts(db: Session, user: User) -> EmailCounts:
    ensure_sample_emails(db, user)
    return EmailCounts(**email_repo.get_counts(db, user.id))
