from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from app.models.database import Document, DocumentVersion, Job, JobStatus
from app.core.logging import logger


class SyncJobRepository:
    """Synchronous Job repository for Celery workers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def update_status(
        self, 
        job_id: int, 
        status: JobStatus,
        error_message: Optional[str] = None
    ) -> Optional[Job]:
        """Update job status"""
        job = self.get_by_id(job_id)
        if not job:
            return None
        
        job.status = status
        
        if status == JobStatus.PROCESSING:
            job.started_at = datetime.utcnow()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            job.completed_at = datetime.utcnow()
        
        if error_message:
            job.error_message = error_message
        
        self.db.flush()
        logger.info(f"Job {job_id} status updated to {status}")
        
        return job
    
    def save_patch(self, job_id: int, patch_json: str) -> Optional[Job]:
        """Save patch JSON to job"""
        job = self.get_by_id(job_id)
        if not job:
            return None
        
        job.patch_json = patch_json
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        
        self.db.flush()
        logger.info(f"Patch saved for job {job_id}")
        
        return job


class SyncDocumentRepository:
    """Synchronous Document repository for Celery workers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(Document.id == document_id).first()
