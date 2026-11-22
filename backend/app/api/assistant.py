from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.assistant import (
    AssistantConversationCreate,
    AssistantConversationListResponse,
    AssistantConversationResponse,
    AssistantMessageCreate,
    AssistantMessageResponse,
)
from app.services import assistant as assistant_service


router = APIRouter()


@router.post("/conversations", response_model=AssistantConversationResponse)
def create_conversation(
    data: AssistantConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssistantConversationResponse:
    conversation = assistant_service.create_conversation(db, current_user, data)
    return assistant_service.get_conversation(db, current_user, conversation.id)


@router.get("/conversations", response_model=AssistantConversationListResponse)
def list_conversations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssistantConversationListResponse:
    return assistant_service.list_conversations(db, current_user, page, page_size)


@router.get("/conversations/{conversation_id}", response_model=AssistantConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssistantConversationResponse:
    return assistant_service.get_conversation(db, current_user, conversation_id)


@router.post("/conversations/{conversation_id}/messages", response_model=AssistantMessageResponse)
def send_message(
    conversation_id: int,
    data: AssistantMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssistantMessageResponse:
    return assistant_service.send_message(db, current_user, conversation_id, data)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    assistant_service.delete_conversation(db, current_user, conversation_id)
