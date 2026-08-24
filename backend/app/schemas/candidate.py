from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from app.schemas.analysis import CandidateAnalysisResponse


class ExperienceEntry(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    years: Optional[float] = None
    description: Optional[str] = None


class EducationEntry(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    field_of_study: Optional[str] = None


class ProjectEntry(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class CandidateBase(BaseModel):
    name: str = "Unknown Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    total_years_experience: Optional[int] = 0


class CandidateResponse(CandidateBase):
    id: int
    resume_id: int
    job_id: Optional[int] = None
    created_at: datetime
    analysis: Optional[CandidateAnalysisResponse] = None

    model_config = {"from_attributes": True}


class CandidateRankItem(BaseModel):
    rank: int
    candidate_id: int
    resume_id: int
    name: str
    email: Optional[str] = None
    overall_score: float
    recommendation: str
    is_shortlisted: bool
    key_strength: str
    major_gap: str
    total_years_experience: Optional[int] = 0
    matched_skills_count: int = 0
    missing_skills_count: int = 0
