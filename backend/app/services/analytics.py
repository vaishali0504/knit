from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import analytics as analytics_repo
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    CachedAIInsights,
    EmailActivityDay,
    EmailCategoryMetric,
    EmailSummaryMetrics,
    RecentActivityItem,
    TaskSummaryMetrics,
    UpcomingDeadline,
)


CATEGORY_ORDER = (
    "internship",
    "interview",
    "college",
    "important",
    "personal",
    "promotions",
    "updates",
    "suspicious",
    "other",
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _recent_activity(db: Session, user_id: int) -> list[RecentActivityItem]:
    items: list[RecentActivityItem] = []
    for email in analytics_repo.get_recent_emails(db, user_id):
        items.append(RecentActivityItem(
            type="email",
            id=email.id,
            email_id=email.id,
            title=email.subject,
            detail=f"From {email.sender_name}",
            timestamp=_as_utc(email.received_at),
            category=email.category,
        ))
    for task in analytics_repo.get_recent_tasks(db, user_id):
        items.append(RecentActivityItem(
            type="task",
            id=task.id,
            task_id=task.id,
            title=task.title,
            detail=f"Task updated · {task.status.replace('_', ' ')}",
            timestamp=_as_utc(task.updated_at),
            status=task.status,
            priority=task.priority,
        ))
    items.sort(key=lambda item: item.timestamp, reverse=True)
    return items[:10]


def get_overview(db: Session, user: User) -> AnalyticsOverviewResponse:
    now = utc_now()
    today = now.date()
    start_day = today - timedelta(days=29)
    start_at = datetime.combine(start_day, time.min, tzinfo=timezone.utc)
    seven_days = now + timedelta(days=7)

    email_counts = analytics_repo.get_email_summary(db, user.id)
    raw_categories = dict(analytics_repo.get_email_category_counts(db, user.id))
    category_order = list(CATEGORY_ORDER)
    category_order.extend(sorted(set(raw_categories) - set(CATEGORY_ORDER)))
    categories = [
        EmailCategoryMetric(category=category, count=raw_categories.get(category, 0))
        for category in category_order
    ]

    activity_counts = {
        (day if isinstance(day, date) else date.fromisoformat(str(day))): count
        for day, count in analytics_repo.get_email_activity(db, user.id, start_at, now)
    }
    activity = [
        EmailActivityDay(date=day, count=activity_counts.get(day, 0))
        for offset in range(30)
        if (day := start_day + timedelta(days=offset)) <= today
    ]

    task_counts = analytics_repo.get_task_summary(db, user.id, now, seven_days)
    deadlines = [
        UpcomingDeadline(
            task_id=task.id,
            title=task.title,
            due_at=_as_utc(task.due_at),
            priority=task.priority,
            status=task.status,
            source_email_id=task.source_email_id,
        )
        for task in analytics_repo.get_upcoming_deadlines(db, user.id, now)
    ]

    return AnalyticsOverviewResponse(
        timezone="UTC",
        activity_start=start_day,
        activity_end=today,
        emails=EmailSummaryMetrics(**email_counts),
        email_categories=categories,
        email_activity=activity,
        tasks=TaskSummaryMetrics(**task_counts),
        upcoming_deadlines=deadlines,
        recent_activity=_recent_activity(db, user.id),
        ai_insights=CachedAIInsights(**analytics_repo.get_cached_ai_insights(db, user.id)),
    )
