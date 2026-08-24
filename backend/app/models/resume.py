from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    file_size = Column(BigInteger, nullable=False, default=0)
    file_type = Column(String(50), nullable=False, default="pdf")
    
    raw_text = Column(Text, nullable=True, default="")
    cleaned_text = Column(Text, nullable=True, default="")
    
    # Raw parsed structure before validation
    parsed_data = Column(JSON, nullable=True, default=dict)
    
    # Status: 'uploaded', 'parsed', 'screened', 'error'
    status = Column(String(50), default="uploaded", nullable=False)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="resumes")
    candidate = relationship("Candidate", back_populates="resume", uselist=False, cascade="all, delete-orphan")
