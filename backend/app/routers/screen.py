from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.analysis import CandidateAnalysis
from app.schemas.candidate import CandidateRankItem
from app.schemas.analysis import CandidateAnalysisResponse
from app.services.screener_service import ScreenerService

router = APIRouter(tags=["Screening & Results"])


class ScreenRequest(BaseModel):
    job_id: int
    candidate_ids: Optional[List[int]] = None


class JobScreeningResultsResponse(BaseModel):
    job_id: int
    job_title: str
    total_resumes: int
    total_processed: int
    total_shortlisted: int
    average_score: float
    ranked_candidates: List[CandidateRankItem]
    score_distribution: Dict[str, int]


@router.post("/api/screen", response_model=List[CandidateAnalysisResponse])
async def run_screening(req: ScreenRequest, db: Session = Depends(get_db)):
    """
    Run semantic screening against a job.
    If candidate_ids is not provided, screens all candidates associated with the job.
    """
    job = db.query(Job).filter(Job.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    if req.candidate_ids:
        analyses = []
        for c_id in req.candidate_ids:
            res = await ScreenerService.screen_candidate(db, c_id, job.id)
            if res:
                analyses.append(res)
        ScreenerService.recalculate_ranks_for_job(db, job.id)
    else:
        analyses = await ScreenerService.screen_all_resumes_for_job(db, job.id)

    return [CandidateAnalysisResponse.model_validate(a) for a in analyses]


@router.get("/api/jobs/{job_id}/results", response_model=JobScreeningResultsResponse)
def get_job_results(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieve ranked candidate results, summary statistics, and distribution for the dashboard.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    # Get ranked items
    ranked = ScreenerService.recalculate_ranks_for_job(db, job_id)
    
    total_resumes = len(job.resumes)
    total_processed = len(ranked)
    total_shortlisted = sum(1 for c in ranked if c.is_shortlisted)
    avg_score = round(sum(c.overall_score for c in ranked) / total_processed, 1) if total_processed > 0 else 0.0

    distribution = {
        "Strong Match": sum(1 for c in ranked if c.recommendation == "Strong Match"),
        "Match": sum(1 for c in ranked if c.recommendation == "Match"),
        "Partial Match": sum(1 for c in ranked if c.recommendation == "Partial Match"),
        "Weak Match": sum(1 for c in ranked if c.recommendation == "Weak Match"),
    }

    return JobScreeningResultsResponse(
        job_id=job.id,
        job_title=job.title,
        total_resumes=total_resumes,
        total_processed=total_processed,
        total_shortlisted=total_shortlisted,
        average_score=avg_score,
        ranked_candidates=ranked,
        score_distribution=distribution
    )
