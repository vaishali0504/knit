from typing import Optional

from sqlalchemy.orm import Session

from app.models.email_analysis import EmailAnalysis


def get_for_email(db: Session, user_id: int, email_id: int) -> Optional[EmailAnalysis]:
    return (
        db.query(EmailAnalysis)
        .filter(EmailAnalysis.user_id == user_id, EmailAnalysis.email_id == email_id)
        .first()
    )


def upsert(db: Session, user_id: int, email_id: int, result, model_name: str) -> EmailAnalysis:
    analysis = get_for_email(db, user_id, email_id)
    if not analysis:
        analysis = EmailAnalysis(user_id=user_id, email_id=email_id)

    analysis.suggested_category = result.classification.category
    analysis.category_confidence = result.classification.confidence
    analysis.category_explanation = result.classification.explanation
    analysis.summary = result.summary.short_summary
    analysis.main_purpose = result.summary.main_purpose
    analysis.important_points = result.summary.important_points
    analysis.required_action = result.summary.required_action
    analysis.relevant_dates = result.summary.relevant_dates
    analysis.extracted = result.extracted.model_dump(mode="json")
    analysis.security_risk = result.security.risk_level
    analysis.security_warning_signs = result.security.warning_signs
    analysis.security_explanation = result.security.explanation
    analysis.model_name = model_name
    analysis.prompt_version = "p5-v1"

    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def set_manual_category(db: Session, analysis: EmailAnalysis, category: str) -> EmailAnalysis:
    analysis.manual_category = category
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
