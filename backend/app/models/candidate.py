from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Core candidate fields extracted from resume
    name = Column(String(255), nullable=False, default="Unknown Candidate")
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Structured resume data (null/empty if not present, never invented)
    skills = Column(JSON, nullable=True, default=list)            # All identified skills
    technical_skills = Column(JSON, nullable=True, default=list)  # Filtered technical/hard skills
    experience = Column(JSON, nullable=True, default=list)        # [{ "title": "...", "company": "...", "years": 2, "description": "..." }]
    education = Column(JSON, nullable=True, default=list)         # [{ "degree": "...", "institution": "...", "year": "..." }]
    projects = Column(JSON, nullable=True, default=list)          # [{ "name": "...", "description": "...", "technologies": [...] }]
    certifications = Column(JSON, nullable=True, default=list)    # ["AWS Certified...", ...]
    total_years_experience = Column(Integer, nullable=True, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="candidate")
    job = relationship("Job", back_populates="candidates")
    analysis = relationship("CandidateAnalysis", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
