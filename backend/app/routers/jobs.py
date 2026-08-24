from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.services.screener_service import ScreenerService

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """Create a new Job Description and parse structured requirements."""
    if len(job_in.raw_text.strip()) < 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description text is too short. Please provide a complete job description."
        )
    
    job = ScreenerService.create_or_parse_job(
        db=db,
        raw_text=job_in.raw_text,
        title=job_in.title,
        company=job_in.company
    )
    
    resp = JobResponse.model_validate(job)
    resp.resume_count = len(job.resumes)
    resp.candidate_count = len(job.candidates)
    return resp


@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """List all jobs."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    results = []
    for j in jobs:
        r = JobResponse.model_validate(j)
        r.resume_count = len(j.resumes)
        r.candidate_count = len(j.candidates)
        results.append(r)
    return results


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get single job details with structured requirements."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    
    r = JobResponse.model_validate(job)
    r.resume_count = len(job.resumes)
    r.candidate_count = len(job.candidates)
    return r
