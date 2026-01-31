from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import logger


class DocumentNotFoundException(Exception):
    """Raised when document is not found"""
    def __init__(self, document_id: int):
        self.document_id = document_id
        super().__init__(f"Document with id {document_id} not found")


class JobNotFoundException(Exception):
    """Raised when job is not found"""
    def __init__(self, job_id: int):
        self.job_id = job_id
        super().__init__(f"Job with id {job_id} not found")


class PatchNotReadyException(Exception):
    """Raised when trying to access patch before it's ready"""
    def __init__(self, job_id: int, current_status: str):
        self.job_id = job_id
        self.current_status = current_status
        super().__init__(f"Patch for job {job_id} is not ready. Current status: {current_status}")


class DocumentProcessingException(Exception):
    """Raised when document processing fails"""
    pass


async def document_not_found_handler(request: Request, exc: DocumentNotFoundException):
    logger.error(f"Document not found: {exc.document_id}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": "Document not found",
            "detail": str(exc),
            "error_code": "DOCUMENT_NOT_FOUND"
        }
    )


async def job_not_found_handler(request: Request, exc: JobNotFoundException):
    logger.error(f"Job not found: {exc.job_id}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": "Job not found",
            "detail": str(exc),
            "error_code": "JOB_NOT_FOUND"
        }
    )


async def patch_not_ready_handler(request: Request, exc: PatchNotReadyException):
    logger.warning(f"Patch not ready: {exc.job_id}, status: {exc.current_status}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": "Patch not ready",
            "detail": str(exc),
            "error_code": "PATCH_NOT_READY",
            "current_status": exc.current_status
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "detail": exc.errors(),
            "error_code": "VALIDATION_ERROR"
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "error_code": "INTERNAL_ERROR"
        }
    )
