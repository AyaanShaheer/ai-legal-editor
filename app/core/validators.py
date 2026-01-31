from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.core.logging import logger


def validate_file_upload(file: UploadFile) -> bool:
    """Validate uploaded file"""
    
    # Check file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = f".{file.filename.split('.')[-1].lower()}"
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (if content_type is available)
    # Note: Actual size check will be done during reading
    logger.info(f"File validation passed: {file.filename}")
    return True


async def validate_file_size(file: UploadFile) -> bytes:
    """Read and validate file size"""
    
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    logger.info(f"File size validation passed: {size_mb:.2f}MB")
    return content
