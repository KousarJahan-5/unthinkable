from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StructuredRequirements(BaseModel):
    title: str = "Software Engineer"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    min_years_experience: Optional[int] = 0
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    domain_requirements: List[str] = Field(default_factory=list)
    location_requirements: Optional[str] = None


class JobCreate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    raw_text: str = Field(..., min_length=15, description="Full Job Description text")


class JobResponse(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    raw_text: str
    structured_requirements: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    resume_count: int = 0
    candidate_count: int = 0

    model_config = {"from_attributes": True}
