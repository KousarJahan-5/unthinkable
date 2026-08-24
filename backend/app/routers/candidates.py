from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateResponse

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


@router.get("", response_model=List[CandidateResponse])
def list_candidates(
    job_id: Optional[int] = Query(None, description="Filter candidates by Job ID"),
    is_shortlisted: Optional[bool] = Query(None, description="Filter by shortlisted status"),
    db: Session = Depends(get_db)
):
    """List candidates with optional filtering."""
    query = db.query(Candidate)
    if job_id is not None:
        query = query.filter(Candidate.job_id == job_id)

    candidates = query.order_by(Candidate.created_at.desc()).all()

    if is_shortlisted is not None:
        candidates = [c for c in candidates if c.analysis and c.analysis.is_shortlisted == is_shortlisted]

    return [CandidateResponse.model_validate(c) for c in candidates]


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Retrieve full structured profile and analysis for a candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")
    return CandidateResponse.model_validate(candidate)
