from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.email import Email
from app.models.user import User
from app.repositories import email as email_repo
from app.repositories import email_analysis as analysis_repo
from app.schemas.ai import AIAnalysisResponse, ExtractedResponse, ManualCategoryRequest
from app.services.gemini import GeminiProviderError, analyze_email_with_gemini


def _owned_email(db: Session, user: User, email_id: int) -> Email:
    email = email_repo.get_owned(db, user.id, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")
    return email


def _response(db: Session, user: User, email_id: int, cached: bool) -> AIAnalysisResponse:
    analysis = analysis_repo.get_for_email(db, user.id, email_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="AI analysis not found.")
    effective = analysis.manual_category or analysis.suggested_category
    return AIAnalysisResponse(
        id=analysis.id,
        email_id=analysis.email_id,
        suggested_category=analysis.suggested_category,
        category_confidence=analysis.category_confidence,
        category_explanation=analysis.category_explanation,
        manual_category=analysis.manual_category,
        effective_category=effective,
        summary=analysis.summary,
        main_purpose=analysis.main_purpose,
        important_points=analysis.important_points,
        required_action=analysis.required_action,
        relevant_dates=analysis.relevant_dates,
        extracted=ExtractedResponse.model_validate(analysis.extracted),
        security_risk=analysis.security_risk,
        security_warning_signs=analysis.security_warning_signs,
        security_explanation=analysis.security_explanation,
        model_name=analysis.model_name,
        prompt_version=analysis.prompt_version,
        cached=cached,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


def get_analysis(db: Session, user: User, email_id: int) -> AIAnalysisResponse:
    _owned_email(db, user, email_id)
    analysis = analysis_repo.get_for_email(db, user.id, email_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="AI analysis has not been generated.")
    return _response(db, user, email_id, cached=True)


def generate_analysis(db: Session, user: User, email_id: int, regenerate: bool = False) -> AIAnalysisResponse:
    email = _owned_email(db, user, email_id)
    existing = analysis_repo.get_for_email(db, user.id, email_id)
    if existing and not regenerate:
        return _response(db, user, email_id, cached=True)

    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis is unavailable because GEMINI_API_KEY is not configured.",
        )

    try:
        result = analyze_email_with_gemini(
            email.sender_name,
            email.sender_email,
            email.subject,
            email.body,
        )
    except GeminiProviderError as exc:
        if exc.kind == "rate_limit":
            raise HTTPException(status_code=429, detail="Gemini rate limit reached. Please retry shortly.")
        if exc.kind in {"network_timeout", "provider_timeout"}:
            raise HTTPException(status_code=504, detail="Gemini request timed out. Please retry.")
        if exc.kind == "sdk_unavailable":
            raise HTTPException(status_code=503, detail="Gemini SDK is unavailable on the backend.")
        if exc.kind == "authentication":
            raise HTTPException(status_code=502, detail="Gemini rejected the configured credentials. Please try again later.")
        raise HTTPException(status_code=502, detail="Gemini is temporarily unavailable. Please try again later.")
    except RuntimeError as exc:
        if "not installed" in str(exc).lower():
            raise HTTPException(status_code=503, detail="Gemini SDK is unavailable on the backend.")
        raise HTTPException(status_code=502, detail="Gemini analysis could not be completed. Please try again later.")

    analysis_repo.upsert(db, user.id, email.id, result, settings.GEMINI_MODEL)
    return _response(db, user, email_id, cached=False)


def set_manual_category(db: Session, user: User, email_id: int, request: ManualCategoryRequest) -> AIAnalysisResponse:
    _owned_email(db, user, email_id)
    analysis = analysis_repo.get_for_email(db, user.id, email_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Generate AI analysis before correcting the category.")
    analysis_repo.set_manual_category(db, analysis, request.category)
    return _response(db, user, email_id, cached=True)
