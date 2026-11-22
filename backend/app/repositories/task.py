from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def base_query(db: Session, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id)


def list_tasks(
    db: Session,
    user_id: int,
    status: Optional[str],
    priority: Optional[str],
    search: Optional[str],
    sort: str,
    page: int,
    page_size: int,
):
    query = base_query(db, user_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))

    if sort == "oldest":
        query = query.order_by(Task.created_at.asc(), Task.id.asc())
    elif sort == "priority":
        query = query.order_by(
            Task.status.asc(),
            case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                else_=3,
            ).asc(),
            Task.due_at.asc().nullslast(),
            Task.created_at.desc(),
        )
    else:
        query = query.order_by(Task.due_at.asc().nullslast(), Task.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_owned(db: Session, user_id: int, task_id: int) -> Optional[Task]:
    return base_query(db, user_id).filter(Task.id == task_id).first()


def create(db: Session, user_id: int, data: TaskCreate) -> Task:
    task = Task(user_id=user_id, **data.model_dump())
    if task.status == "completed":
        task.completed_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update(db: Session, task: Task, data: TaskUpdate) -> Task:
    changes = data.model_dump(exclude_unset=True)
    old_status = task.status
    for key, value in changes.items():
        setattr(task, key, value)
    new_status = changes.get("status", old_status)
    if new_status == "completed" and old_status != "completed":
        task.completed_at = datetime.now(timezone.utc)
    elif new_status != "completed":
        task.completed_at = None
    db.commit()
    db.refresh(task)
    return task


def delete(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
