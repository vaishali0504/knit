from datetime import datetime

from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.email_analysis import EmailAnalysis
from app.models.task import Task


def _active_user_emails(db: Session, user_id: int):
    return db.query(Email).filter(
        Email.user_id == user_id,
        Email.is_deleted.is_(False),
    )


def _user_tasks(db: Session, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id)


def get_email_summary(db: Session, user_id: int) -> dict[str, int]:
    row = _active_user_emails(db, user_id).with_entities(
        func.count(Email.id),
        func.coalesce(func.sum(case((Email.is_read.is_(False), 1), else_=0)), 0),
        func.coalesce(func.sum(case((Email.is_important.is_(True), 1), else_=0)), 0),
    ).one()
    return {"total": int(row[0]), "unread": int(row[1]), "important": int(row[2])}


def get_email_category_counts(db: Session, user_id: int) -> list[tuple[str, int]]:
    rows = (
        _active_user_emails(db, user_id)
        .with_entities(Email.category, func.count(Email.id))
        .group_by(Email.category)
        .all()
    )
    return [(str(category), int(count)) for category, count in rows]


def get_email_activity(
    db: Session,
    user_id: int,
    start_at: datetime,
    end_at: datetime,
) -> list[tuple[str, int]]:
    rows = (
        _active_user_emails(db, user_id)
        .filter(Email.received_at >= start_at, Email.received_at <= end_at)
        .with_entities(func.date(Email.received_at), func.count(Email.id))
        .group_by(func.date(Email.received_at))
        .all()
    )
    return [(str(day), int(count)) for day, count in rows]


def get_task_summary(db: Session, user_id: int, now: datetime, seven_days: datetime) -> dict[str, int]:
    overdue = and_(Task.status != "completed", Task.due_at.is_not(None), Task.due_at < now)
    due_soon = and_(
        Task.status != "completed",
        Task.due_at.is_not(None),
        Task.due_at >= now,
        Task.due_at <= seven_days,
    )
    row = _user_tasks(db, user_id).with_entities(
        func.count(Task.id),
        func.coalesce(func.sum(case((Task.status == "pending", 1), else_=0)), 0),
        func.coalesce(func.sum(case((Task.status == "in_progress", 1), else_=0)), 0),
        func.coalesce(func.sum(case((Task.status == "completed", 1), else_=0)), 0),
        func.coalesce(func.sum(case((overdue, 1), else_=0)), 0),
        func.coalesce(func.sum(case((due_soon, 1), else_=0)), 0),
    ).one()
    return {
        "total": int(row[0]),
        "pending": int(row[1]),
        "in_progress": int(row[2]),
        "completed": int(row[3]),
        "overdue": int(row[4]),
        "due_next_7_days": int(row[5]),
    }


def get_upcoming_deadlines(db: Session, user_id: int, now: datetime, limit: int = 5) -> list[Task]:
    return (
        _user_tasks(db, user_id)
        .filter(Task.status != "completed", Task.due_at.is_not(None), Task.due_at >= now)
        .order_by(Task.due_at.asc(), Task.id.asc())
        .limit(limit)
        .all()
    )


def get_recent_emails(db: Session, user_id: int, limit: int = 5) -> list[Email]:
    return (
        _active_user_emails(db, user_id)
        .order_by(Email.received_at.desc(), Email.id.desc())
        .limit(limit)
        .all()
    )


def get_recent_tasks(db: Session, user_id: int, limit: int = 5) -> list[Task]:
    return (
        _user_tasks(db, user_id)
        .order_by(Task.updated_at.desc(), Task.id.desc())
        .limit(limit)
        .all()
    )


def get_cached_ai_insights(db: Session, user_id: int) -> dict[str, int]:
    row = (
        db.query(
            func.count(EmailAnalysis.id),
            func.coalesce(
                func.sum(case((EmailAnalysis.security_risk == "High", 1), else_=0)),
                0,
            ),
        )
        .join(Email, Email.id == EmailAnalysis.email_id)
        .filter(
            EmailAnalysis.user_id == user_id,
            Email.user_id == user_id,
            Email.is_deleted.is_(False),
        )
        .one()
    )
    return {"analysis_count": int(row[0]), "high_risk_flag_count": int(row[1])}
