from sqlalchemy.orm import Session

from app.models.reply_draft import ReplyDraft


def get_for_email(db: Session, user_id: int, email_id: int) -> ReplyDraft | None:
    return (
        db.query(ReplyDraft)
        .filter(ReplyDraft.user_id == user_id, ReplyDraft.email_id == email_id)
        .first()
    )


def upsert(
    db: Session,
    user_id: int,
    email_id: int,
    tone: str,
    content: str,
) -> ReplyDraft:
    draft = get_for_email(db, user_id, email_id)
    if draft is None:
        draft = ReplyDraft(user_id=user_id, email_id=email_id)
    draft.tone = tone
    draft.content = content
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft
