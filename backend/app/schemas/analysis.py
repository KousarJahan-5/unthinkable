from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class SkillsMatchSchema(BaseModel):
    matched: List[str] = Field(default_factory=list, description="Mandatory and preferred skills candidate clearly possesses")
    partial: List[str] = Field(default_factory=list, description="Related or partially demonstrated skills")
    missing: List[str] = Field(default_factory=list, description="Required or preferred skills missing from candidate's profile")


class SubMatchScore(BaseModel):
    score: float = Field(default=5.0, ge=0.0, le=10.0, description="Score from 0 to 10")
    summary: str = Field(default="", description="Concise assessment summary")

    @field_validator("score", mode="before")
    @classmethod
    def validate_subscore(cls, v: Union[int, float, str]) -> float:
        try:
            val = float(v)
            return max(0.0, min(10.0, val))
        except (ValueError, TypeError):
            return 5.0


class CandidateAnalysisOutput(BaseModel):
    """Exact schema enforced on LLM output and scoring validation."""
    candidate_name: str = Field(default="Candidate", description="Name of candidate")
    overall_score: float = Field(default=5.0, ge=1.0, le=10.0, description="Normalized score 1.0 - 10.0")
    recommendation: str = Field(default="Partial Match", description="Strong Match | Match | Partial Match | Weak Match")
    skills_match: SkillsMatchSchema = Field(default_factory=SkillsMatchSchema)
    experience_match: SubMatchScore = Field(default_factory=SubMatchScore)
    education_match: SubMatchScore = Field(default_factory=SubMatchScore)
    relevant_projects: List[Union[str, dict]] = Field(default_factory=list, description="Highlight projects matching JD domain")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths")
    gaps: List[str] = Field(default_factory=list, description="Key candidate gaps or missing skills")
    justification: str = Field(default="", description="Concise recruiter-oriented justification")

    @field_validator("overall_score", mode="before")
    @classmethod
    def validate_score(cls, v: Union[int, float, str]) -> float:
        try:
            val = float(v)
            return round(max(1.0, min(10.0, val)), 1)
        except (ValueError, TypeError):
            return 5.0

    @field_validator("recommendation", mode="before")
    @classmethod
    def validate_recommendation(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            return "Partial Match"
        clean = v.strip().title()
        valid = ["Strong Match", "Partial Match", "Weak Match", "Match"]
        for item in valid:
            if item.lower() in clean.lower():
                return item
        return "Partial Match"


class CandidateAnalysisResponse(CandidateAnalysisOutput):
    id: int
    candidate_id: int
    job_id: int
    is_shortlisted: bool = False
    rank: Optional[int] = None
    evaluation_mode: str = "llm"

    model_config = {"from_attributes": True}
