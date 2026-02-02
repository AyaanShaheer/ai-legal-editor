from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime
from app.models.database import Job, JobStatus
from app.repositories.base import BaseRepository
from app.core.logging import logger


class JobRepository(BaseRepository[Job]):
    """Repository for Job model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Job, db)
    
    async def get_by_document(
        self, 
        document_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """
        Get all jobs for a document
        
        Args:
            document_id: Document ID
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of jobs
        """
        result = await self.db.execute(
            select(Job)
            .where(Job.document_id == document_id)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        jobs = result.scalars().all()
        logger.info(f"Retrieved {len(jobs)} jobs for document {document_id}")
        return list(jobs)
    
    async def get_by_status(self, status: JobStatus) -> List[Job]:
        """
        Get all jobs with specific status
        
        Args:
            status: Job status
            
        Returns:
            List of jobs
        """
        result = await self.db.execute(
            select(Job)
            .where(Job.status == status)
            .order_by(Job.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def update_status(
        self, 
        job_id: int, 
        status: JobStatus,
        error_message: Optional[str] = None
    ) -> Optional[Job]:
        """
        Update job status
        
        Args:
            job_id: Job ID
            status: New status
            error_message: Error message if failed
            
        Returns:
            Updated job or None
        """
        update_data = {"status": status}
        
        if status == JobStatus.PROCESSING and not error_message:
            update_data["started_at"] = datetime.utcnow()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow()
        
        if error_message:
            update_data["error_message"] = error_message
        
        updated = await self.update(job_id, **update_data)
        
        if updated:
            logger.info(f"Job {job_id} status updated to {status}")
        
        return updated
    
    async def save_patch(self, job_id: int, patch_json: str) -> Optional[Job]:
        """
        Save patch JSON to job
        
        Args:
            job_id: Job ID
            patch_json: JSON string of patches
            
        Returns:
            Updated job or None
        """
        return await self.update(
            job_id,
            patch_json=patch_json,
            status=JobStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )
    
    async def get_pending_jobs(self, limit: int = 10) -> List[Job]:
        """
        Get pending jobs for processing
        
        Args:
            limit: Maximum number of jobs
            
        Returns:
            List of pending jobs
        """
        result = await self.db.execute(
            select(Job)
            .where(Job.status == JobStatus.PENDING)
            .order_by(Job.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_stuck_jobs(self, timeout_minutes: int = 30) -> List[Job]:
        """
        Get jobs stuck in processing state
        
        Args:
            timeout_minutes: Timeout threshold
            
        Returns:
            List of stuck jobs
        """
        cutoff_time = datetime.utcnow()
        # Subtract timeout_minutes
        from datetime import timedelta
        cutoff_time = cutoff_time - timedelta(minutes=timeout_minutes)
        
        result = await self.db.execute(
            select(Job)
            .where(
                and_(
                    Job.status == JobStatus.PROCESSING,
                    Job.started_at < cutoff_time
                )
            )
        )
        return list(result.scalars().all())
    
    async def count_by_status(self, status: JobStatus) -> int:
        """
        Count jobs by status
        
        Args:
            status: Job status
            
        Returns:
            Job count
        """
        result = await self.db.execute(
            select(Job).where(Job.status == status)
        )
        return len(result.scalars().all())
