from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class EmailSummaryMetrics(BaseModel):
    total: int
    unread: int
    important: int


class EmailCategoryMetric(BaseModel):
    category: str
    count: int


class EmailActivityDay(BaseModel):
    date: date
    count: int


class TaskSummaryMetrics(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    overdue: int
    due_next_7_days: int


class UpcomingDeadline(BaseModel):
    task_id: int
    title: str
    due_at: datetime
    priority: str
    status: str
    source_email_id: int | None


class RecentActivityItem(BaseModel):
    type: Literal["email", "task"]
    id: int
    title: str
    detail: str
    timestamp: datetime
    category: str | None = None
    status: str | None = None
    priority: str | None = None
    email_id: int | None = None
    task_id: int | None = None


class CachedAIInsights(BaseModel):
    analysis_count: int
    high_risk_flag_count: int


class AnalyticsOverviewResponse(BaseModel):
    timezone: Literal["UTC"]
    activity_start: date
    activity_end: date
    emails: EmailSummaryMetrics
    email_categories: list[EmailCategoryMetric]
    email_activity: list[EmailActivityDay]
    tasks: TaskSummaryMetrics
    upcoming_deadlines: list[UpcomingDeadline]
    recent_activity: list[RecentActivityItem]
    ai_insights: CachedAIInsights
