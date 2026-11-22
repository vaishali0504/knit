from typing import Optional

from sqlalchemy.orm import Session

from app.models.assistant import AIConversation, AIMessage, AIMessageReference


def get_conversation(db: Session, user_id: int, conversation_id: int) -> Optional[AIConversation]:
    return (
        db.query(AIConversation)
        .filter(AIConversation.id == conversation_id, AIConversation.user_id == user_id)
        .first()
    )


def create_conversation(db: Session, user_id: int, title: str) -> AIConversation:
    conversation = AIConversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, user_id: int, page: int, page_size: int):
    query = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == user_id)
        .order_by(AIConversation.updated_at.desc(), AIConversation.id.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def add_message(
    db: Session,
    conversation: AIConversation,
    user_id: int,
    role: str,
    content: str,
) -> AIMessage:
    message = AIMessage(
        conversation_id=conversation.id,
        user_id=user_id,
        role=role,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def add_references(db: Session, message: AIMessage, email_ids: list[int]) -> None:
    for email_id in dict.fromkeys(email_ids):
        db.add(AIMessageReference(message_id=message.id, email_id=email_id))
    db.commit()
    db.refresh(message)


def delete_conversation(db: Session, conversation: AIConversation) -> None:
    db.delete(conversation)
    db.commit()
