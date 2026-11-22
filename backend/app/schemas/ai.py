from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


EmailCategory = Literal[
    "Internship", "Interview", "College", "Important", "Personal",
    "Promotions", "Updates", "Suspicious", "Other",
]


class ClassificationOutput(BaseModel):
    category: EmailCategory
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str = Field(min_length=1, max_length=500)


class SummaryOutput(BaseModel):
    short_summary: str = Field(min_length=1, max_length=1000)
    main_purpose: str = Field(min_length=1, max_length=500)
    important_points: List[str] = Field(default_factory=list)
    required_action: Optional[str] = None
    relevant_dates: List[str] = Field(default_factory=list)


class ExtractedInformation(BaseModel):
    person_or_organization: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    eligibility: List[str] = Field(default_factory=list)
    stipend_or_compensation: Optional[str] = None
    application_deadline: Optional[str] = None
    interview_date_time: Optional[str] = None
    event_date: Optional[str] = None
    event_location: Optional[str] = None
    application_or_registration_url: Optional[str] = None
    required_documents: List[str] = Field(default_factory=list)
    contact_information: Optional[str] = None
    next_action: Optional[str] = None


class SecurityOutput(BaseModel):
    risk_level: Literal["Low", "Medium", "High"]
    warning_signs: List[str] = Field(default_factory=list)
    explanation: str = Field(min_length=1, max_length=500)


class AIAnalysisOutput(BaseModel):
    classification: ClassificationOutput
    summary: SummaryOutput
    extracted: ExtractedInformation
    security: SecurityOutput


class ExtractedResponse(BaseModel):
    person_or_organization: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    eligibility: List[str] = Field(default_factory=list)
    stipend_or_compensation: Optional[str] = None
    application_deadline: Optional[str] = None
    interview_date_time: Optional[str] = None
    event_date: Optional[str] = None
    event_location: Optional[str] = None
    application_or_registration_url: Optional[str] = None
    required_documents: List[str] = Field(default_factory=list)
    contact_information: Optional[str] = None
    next_action: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    id: int
    email_id: int
    suggested_category: str
    category_confidence: float
    category_explanation: str
    manual_category: Optional[str] = None
    effective_category: str
    summary: str
    main_purpose: str
    important_points: List[str]
    required_action: Optional[str]
    relevant_dates: List[str]
    extracted: ExtractedResponse
    security_risk: str
    security_warning_signs: List[str]
    security_explanation: str
    model_name: str
    prompt_version: str
    cached: bool
    created_at: datetime
    updated_at: datetime


class ManualCategoryRequest(BaseModel):
    category: EmailCategory
