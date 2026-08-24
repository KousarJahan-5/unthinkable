from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, default="Untitled Position")
    company = Column(String(255), nullable=True, default="")
    raw_text = Column(Text, nullable=False)
    
    # Structured requirements extracted from JD
    # e.g., { "required_skills": [...], "preferred_skills": [...], "min_years_experience": 3, "education": [...], "responsibilities": [...], "domain": [...] }
    structured_requirements = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    resumes = relationship("Resume", back_populates="job", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")
    analyses = relationship("CandidateAnalysis", back_populates="job", cascade="all, delete-orphan")
