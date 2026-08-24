from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    id: int
    job_id: Optional[int] = None
    filename: str
    file_size: int
    file_type: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    candidate_id: Optional[int] = None
    candidate_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ResumeDetailResponse(ResumeUploadResponse):
    raw_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
