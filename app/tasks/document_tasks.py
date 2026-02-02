from celery import Task
import json
from typing import Dict, Any
from app.core.celery_app import celery_app
from app.core.database import sync_session_maker
from app.repositories.sync_repositories import SyncJobRepository, SyncDocumentRepository
from app.services import (
    AzureStorageService,
    DOCXParser,
    get_legal_agent,
    ParagraphPatchGenerator
)
from app.models.database import JobStatus
from app.core.logging import logger


@celery_app.task(name="process_edit_instruction")
def process_edit_instruction(job_id: int) -> Dict[str, Any]:
    """
    Process edit instruction asynchronously
    
    Args:
        job_id: Job ID to process
        
    Returns:
        Result dictionary
    """
    
    logger.info(f"Starting job processing: {job_id}")
    
    # Get database session
    db = sync_session_maker()
    
    try:
        # Get repositories (sync versions)
        job_repo = SyncJobRepository(db)
        doc_repo = SyncDocumentRepository(db)
        
        # Get job
        job = job_repo.get_by_id(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"success": False, "error": "Job not found"}
        
        # Update status to processing
        job_repo.update_status(job_id, JobStatus.PROCESSING)
        db.commit()
        
        logger.info(f"Job {job_id} status: PROCESSING")
        
        # Get document
        document = doc_repo.get_by_id(job.document_id)
        if not document:
            logger.error(f"Document {job.document_id} not found")
            job_repo.update_status(
                job_id, 
                JobStatus.FAILED, 
                error_message="Document not found"
            )
            db.commit()
            return {"success": False, "error": "Document not found"}
        
        # Download document from storage
        logger.info(f"Downloading document from: {document.blob_path}")
        storage = AzureStorageService()
        document_bytes = storage.download_document(document.blob_path)
        
        # Parse document
        logger.info("Parsing document...")
        parser = DOCXParser(document_bytes)
        parsed_data = parser.parse()
        
        logger.info(f"Parsed {parsed_data['total_paragraphs']} paragraphs")
        
        # Get LLM agent
        logger.info("Initializing LLM agent...")
        agent = get_legal_agent()
        
        # Generate edits
        logger.info(f"Generating edits for instruction: {job.instruction[:100]}...")
        edits = agent.generate_edits(
            document_paragraphs=parsed_data["paragraphs"],
            instruction=job.instruction
        )
        
        logger.info(f"Generated {len(edits)} edits")
        
        if not edits:
            logger.warning("No edits generated")
            job_repo.update_status(
                job_id,
                JobStatus.COMPLETED,
                error_message="No changes needed for this instruction"
            )
            db.commit()
            return {
                "success": True,
                "edits_count": 0,
                "message": "No changes needed"
            }
        
        # Generate patches
        logger.info("Generating patches...")
        patch_generator = ParagraphPatchGenerator()
        patches = patch_generator.generate_paragraph_patches(edits)
        
        # Validate patches
        all_valid = patch_generator.validate_all_patches(patches)
        
        if not all_valid:
            logger.error("Patch validation failed")
            job_repo.update_status(
                job_id,
                JobStatus.FAILED,
                error_message="Generated patches failed validation"
            )
            db.commit()
            return {"success": False, "error": "Patch validation failed"}
        
        # Save patches as JSON
        patch_json = json.dumps({"patches": patches})
        
        job_repo.save_patch(job_id, patch_json)
        db.commit()
        
        logger.info(f"Job {job_id} completed successfully with {len(patches)} patches")
        
        return {
            "success": True,
            "job_id": job_id,
            "edits_count": len(patches),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
        
        # Update job status to failed
        try:
            job_repo = SyncJobRepository(db)
            job_repo.update_status(
                job_id,
                JobStatus.FAILED,
                error_message=str(e)
            )
            db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update job status: {str(db_error)}")
        
        return {
            "success": False,
            "job_id": job_id,
            "error": str(e)
        }
    
    finally:
        db.close()


@celery_app.task(name="cleanup_old_jobs")
def cleanup_old_jobs(days: int = 30) -> Dict[str, Any]:
    """
    Cleanup old completed/failed jobs
    
    Args:
        days: Delete jobs older than this many days
        
    Returns:
        Cleanup result
    """
    
    logger.info(f"Starting cleanup of jobs older than {days} days")
    
    # TODO: Implement cleanup logic
    
    return {
        "success": True,
        "deleted_count": 0,
        "message": "Cleanup not yet implemented"
    }
