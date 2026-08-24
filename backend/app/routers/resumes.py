import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse, ResumeDetailResponse
from app.utils.security import sanitize_filename, validate_file_upload, validate_file_size
from app.services.screener_service import ScreenerService

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.post("/upload", response_model=List[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload one or multiple resumes (PDF, TXT, MD).
    Validates file formats, file sizes, extracts candidate information, and saves to database.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided for upload."
        )

    responses: List[ResumeUploadResponse] = []

    for file in files:
        # Validate format
        validate_file_upload(file)

        # Read content safely
        content = await file.read()
        validate_file_size(len(content))

        # Sanitize filename & save copy to uploads dir
        safe_name = sanitize_filename(file.filename or "resume.pdf")
        disk_path = os.path.join(settings.UPLOADS_DIR, safe_name)
        try:
            with open(disk_path, "wb") as f:
                f.write(content)
        except Exception:
            disk_path = None

        # Process and parse resume
        resume_record = ScreenerService.process_and_save_resume(
            db=db,
            job_id=job_id,
            filename=file.filename or safe_name,
            file_bytes=content,
            file_path=disk_path
        )

        resp = ResumeUploadResponse.model_validate(resume_record)
        if resume_record.candidate:
            resp.candidate_id = resume_record.candidate.id
            resp.candidate_name = resume_record.candidate.name

        responses.append(resp)

    return responses


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Retrieve resume details and extracted text."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    
    resp = ResumeDetailResponse.model_validate(resume)
    if resume.candidate:
        resp.candidate_id = resume.candidate.id
        resp.candidate_name = resume.candidate.name
    return resp
