from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai import AIAnalysisResponse, ManualCategoryRequest
from app.schemas.reply import (
    ReplyDraftResponse,
    ReplyDraftUpdate,
    ReplyGenerationRequest,
    ReplyGenerationResponse,
)
from app.services import ai_analysis
from app.services import reply_generation
from app.services.gemini import GeminiProviderError, ping_gemini_text
from app.core.config import settings

router = APIRouter()


@router.get("/connection")
def check_ai_connection(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY is not configured.",
        )
    try:
        response_text = ping_gemini_text()
    except GeminiProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.safe_message or "Gemini provider connection failed.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return {
        "status": "connected",
        "model": settings.GEMINI_MODEL,
        "response": response_text,
    }


@router.get("/emails/{email_id}/analysis", response_model=AIAnalysisResponse)
def get_email_analysis(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIAnalysisResponse:
    return ai_analysis.get_analysis(db, current_user, email_id)


@router.post("/emails/{email_id}/analyze", response_model=AIAnalysisResponse)
def analyze_email(
    email_id: int,
    regenerate: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIAnalysisResponse:
    return ai_analysis.generate_analysis(db, current_user, email_id, regenerate=regenerate)


@router.patch("/emails/{email_id}/category", response_model=AIAnalysisResponse)
def correct_category(
    email_id: int,
    request: ManualCategoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIAnalysisResponse:
    return ai_analysis.set_manual_category(db, current_user, email_id, request)


@router.post("/emails/{email_id}/reply", response_model=ReplyGenerationResponse)
def generate_email_reply(
    email_id: int,
    request: ReplyGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReplyGenerationResponse:
    return reply_generation.generate_reply(db, current_user, email_id, request.tone)


@router.get("/emails/{email_id}/reply-draft", response_model=ReplyDraftResponse | None)
def get_email_reply_draft(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReplyDraftResponse | None:
    return reply_generation.get_reply_draft(db, current_user, email_id)


@router.put("/emails/{email_id}/reply-draft", response_model=ReplyDraftResponse)
def save_email_reply_draft(
    email_id: int,
    request: ReplyDraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReplyDraftResponse:
    return reply_generation.save_reply_draft(db, current_user, email_id, request)
