import os
import re
import uuid
from fastapi import HTTPException, UploadFile, status
from app.config import settings


def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filename to prevent directory traversal and special character injection:
    - Strip directory paths
    - Replace whitespace and illegal characters with underscores
    - Prefix with a short UUID to avoid collisions
    """
    if not filename:
        return f"resume_{uuid.uuid4().hex[:8]}.pdf"

    # Get basename only
    base = os.path.basename(filename)
    
    # Split name and extension
    name, ext = os.path.splitext(base)
    ext = ext.lower().strip()
    
    # Remove unsafe characters from name
    cleaned_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)
    cleaned_name = re.sub(r'_+', '_', cleaned_name).strip('_')
    
    if not cleaned_name:
        cleaned_name = "resume"
        
    return f"{cleaned_name}_{uuid.uuid4().hex[:6]}{ext}"


def validate_file_upload(file: UploadFile) -> None:
    """
    Validate uploaded file extension and content type:
    - Check against allowed extensions
    - Throw descriptive 400 Bad Request on violation
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    _, ext = os.path.splitext(file.filename)
    clean_ext = ext.lower().lstrip(".")

    allowed = settings.allowed_extensions_list
    if clean_ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '.{clean_ext}' is not supported. Allowed extensions: {', '.join(allowed)}"
        )


def validate_file_size(size_bytes: int) -> None:
    """Validate that file does not exceed maximum configured file size."""
    if size_bytes > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB}MB."
        )
