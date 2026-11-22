from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCounts, TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services import task as task_service


router = APIRouter()


@router.get("/counts", response_model=TaskCounts)
def get_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskCounts:
    return task_service.get_counts(db, current_user)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=200),
    sort: str = Query(default="due", pattern="^(due|oldest|priority)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskListResponse:
    return task_service.list_tasks(
        db,
        current_user,
        status=status_filter,
        priority=priority,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    return task_service.create_task(db, current_user, data)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    return task_service.get_task(db, current_user, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    return task_service.update_task(db, current_user, task_id, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    task_service.delete_task(db, current_user, task_id)
