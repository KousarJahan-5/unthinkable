from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CandidateAnalysis(Base):
    __tablename__ = "candidate_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Core scores & recommendation (Normalized 1.0 - 10.0)
    overall_score = Column(Float, nullable=False, default=1.0)
    recommendation = Column(String(50), nullable=False, default="Weak Match")  # "Strong Match" | "Match" | "Partial Match" | "Weak Match"
    is_shortlisted = Column(Boolean, default=False, nullable=False)
    rank = Column(Integer, nullable=True)

    # Detailed sub-scores & structured matches
    # { "matched": [...], "partial": [...], "missing": [...] }
    skills_match = Column(JSON, nullable=True, default=dict)
    
    # { "score": 8.5, "summary": "..." }
    experience_match = Column(JSON, nullable=True, default=dict)
    
    # { "score": 9.0, "summary": "..." }
    education_match = Column(JSON, nullable=True, default=dict)
    
    # [{ "name": "...", "relevance": "..." }]
    relevant_projects = Column(JSON, nullable=True, default=list)

    # Key highlights & gaps
    strengths = Column(JSON, nullable=True, default=list)
    gaps = Column(JSON, nullable=True, default=list)
    
    # Concise recruiter justification
    justification = Column(Text, nullable=False, default="")
    
    # Audit log (no API keys, just raw JSON response from evaluation)
    raw_llm_response = Column(JSON, nullable=True)
    evaluation_mode = Column(String(50), default="llm", nullable=False)  # "llm" or "heuristic_fallback"

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="analysis")
    job = relationship("Job", back_populates="analyses")
