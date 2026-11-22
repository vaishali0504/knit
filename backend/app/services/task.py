from math import ceil
from typing import Optional

from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.task import Task
from app.models.user import User
from app.repositories import task as task_repo
from app.schemas.task import TaskCounts, TaskCreate, TaskListResponse, TaskResponse, TaskUpdate


VALID_STATUSES = {"pending", "in_progress", "completed"}
VALID_PRIORITIES = {"low", "medium", "high"}


def _owned_task(db: Session, user: User, task_id: int) -> Task:
    task = task_repo.get_owned(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


def _validate_source_email(db: Session, user: User, source_email_id: Optional[int]) -> None:
    if source_email_id is None:
        return
    email = db.query(Email).filter(
        Email.id == source_email_id,
        Email.user_id == user.id,
        Email.is_deleted.is_(False),
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Source email not found.")


def list_tasks(
    db: Session,
    user: User,
    status: Optional[str],
    priority: Optional[str],
    search: Optional[str],
    sort: str,
    page: int,
    page_size: int,
) -> TaskListResponse:
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid task status.")
    if priority and priority not in VALID_PRIORITIES:
        raise HTTPException(status_code=422, detail="Invalid task priority.")
    if sort not in {"due", "oldest", "priority"}:
        raise HTTPException(status_code=422, detail="Invalid task sort.")
    items, total = task_repo.list_tasks(
        db,
        user.id,
        status=status,
        priority=priority,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return TaskListResponse(
        items=[TaskResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, ceil(total / page_size)),
    )


def create_task(db: Session, user: User, data: TaskCreate) -> Task:
    _validate_source_email(db, user, data.source_email_id)
    return task_repo.create(db, user.id, data)


def get_task(db: Session, user: User, task_id: int) -> Task:
    return _owned_task(db, user, task_id)


def update_task(db: Session, user: User, task_id: int, data: TaskUpdate) -> Task:
    task = _owned_task(db, user, task_id)
    _validate_source_email(db, user, data.source_email_id)
    return task_repo.update(db, task, data)


def delete_task(db: Session, user: User, task_id: int) -> None:
    task = _owned_task(db, user, task_id)
    task_repo.delete(db, task)


def get_counts(db: Session, user: User) -> TaskCounts:
    query = task_repo.base_query(db, user.id)
    now = datetime.now(timezone.utc)
    week = now + timedelta(days=7)
    return TaskCounts(
        all=query.count(),
        pending=query.filter(Task.status == "pending").count(),
        in_progress=query.filter(Task.status == "in_progress").count(),
        completed=query.filter(Task.status == "completed").count(),
        upcoming=query.filter(
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at >= now,
            Task.due_at <= week,
        ).count(),
    )
