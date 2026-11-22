from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import case, desc, or_
from sqlalchemy.orm import Session

from app.models.email import Email


def base_query(db: Session, user_id: int):
    return db.query(Email).filter(Email.user_id == user_id)


def list_emails(
    db: Session,
    user_id: int,
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "newest",
    page: int = 1,
    page_size: int = 20,
    deleted: bool = False,
):
    query = base_query(db, user_id).filter(Email.is_deleted == deleted)

    if category:
        if category.lower() == "important":
            query = query.filter(Email.is_important.is_(True))
        else:
            query = query.filter(Email.category == category.lower())

    if status:
        if status.lower() == "read":
            query = query.filter(Email.is_read.is_(True))
        elif status.lower() == "unread":
            query = query.filter(Email.is_read.is_(False))

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Email.sender_name.ilike(pattern),
                Email.sender_email.ilike(pattern),
                Email.subject.ilike(pattern),
                Email.body.ilike(pattern),
            )
        )

    if sort == "oldest":
        query = query.order_by(Email.received_at.asc(), Email.id.asc())
    else:
        query = query.order_by(Email.received_at.desc(), Email.id.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_owned(db: Session, user_id: int, email_id: int, include_deleted: bool = False) -> Optional[Email]:
    query = base_query(db, user_id).filter(Email.id == email_id)
    if not include_deleted:
        query = query.filter(Email.is_deleted.is_(False))
    return query.first()


def set_read(db: Session, email: Email, is_read: bool) -> Email:
    email.is_read = is_read
    if email.connected_account_id is not None:
        email.is_read_user_modified = True
    db.commit()
    db.refresh(email)
    return email


def set_important(db: Session, email: Email, is_important: bool) -> Email:
    email.is_important = is_important
    if email.connected_account_id is not None:
        email.is_important_user_modified = True
    db.commit()
    db.refresh(email)
    return email


def soft_delete(db: Session, email: Email) -> Email:
    email.is_deleted = True
    email.deleted_at = datetime.now(timezone.utc)
    if email.connected_account_id is not None:
        email.is_deleted_user_modified = True
    db.commit()
    db.refresh(email)
    return email


def restore(db: Session, email: Email) -> Email:
    email.is_deleted = False
    email.deleted_at = None
    if email.connected_account_id is not None:
        email.is_deleted_user_modified = True
    db.commit()
    db.refresh(email)
    return email


def permanent_delete(db: Session, email: Email) -> None:
    db.delete(email)
    db.commit()


def get_counts(db: Session, user_id: int) -> dict:
    active = base_query(db, user_id).filter(Email.is_deleted.is_(False))
    result = {
        "all": active.count(),
        "internship": active.filter(Email.category == "internship").count(),
        "interview": active.filter(Email.category == "interview").count(),
        "college": active.filter(Email.category == "college").count(),
        "important": active.filter(Email.is_important.is_(True)).count(),
        "personal": active.filter(Email.category == "personal").count(),
        "promotions": active.filter(Email.category == "promotions").count(),
        "updates": active.filter(Email.category == "updates").count(),
        "suspicious": active.filter(Email.category == "suspicious").count(),
        "other": active.filter(Email.category == "other").count(),
        "unread": active.filter(Email.is_read.is_(False)).count(),
        "deleted": base_query(db, user_id).filter(Email.is_deleted.is_(True)).count(),
    }
    return result
