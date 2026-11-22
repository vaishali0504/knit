from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.email import Email
from app.models.user import User
from app.schemas.email import EmailActionResponse, EmailCounts, EmailListResponse, EmailResponse
from app.services import email as email_service

router = APIRouter()


@router.get("", response_model=EmailListResponse)
def list_emails(
    category: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    search: Optional[str] = Query(default=None, max_length=200),
    sort: str = Query(default="newest", pattern="^(newest|oldest)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmailListResponse:
    return email_service.list_emails(
        db,
        current_user,
        category=category,
        status_filter=status_filter,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
        deleted=deleted,
    )


@router.get("/counts", response_model=EmailCounts)
def get_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmailCounts:
    return email_service.get_counts(db, current_user)


@router.get("/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Email:
    return email_service.get_email(db, current_user, email_id)


@router.patch("/{email_id}/read", response_model=EmailActionResponse)
def set_read(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Email:
    return email_service.set_read_status(db, current_user, email_id, True)


@router.patch("/{email_id}/unread", response_model=EmailActionResponse)
def set_unread(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Email:
    return email_service.set_read_status(db, current_user, email_id, False)


@router.patch("/{email_id}/important", response_model=EmailActionResponse)
def set_important(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Email:
    return email_service.set_important_status(db, current_user, email_id, True)


@router.patch("/{email_id}/unimportant", response_model=EmailActionResponse)
def set_unimportant(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Email:
    return email_service.set_important_status(db, current_user, email_id, False)


@router.delete("/{email_id}", response_model=EmailActionResponse)
def delete_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Email:
    return email_service.soft_delete(db, current_user, email_id)


@router.post("/{email_id}/restore", response_model=EmailActionResponse)
def restore_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Email:
    return email_service.restore(db, current_user, email_id)


@router.delete("/{email_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    email_service.permanent_delete(db, current_user, email_id)
