"""
Celery worker entry point
Run with: celery -A worker.celery_app worker --loglevel=info
"""

from app.core.celery_app import celery_app
from app.tasks import process_edit_instruction, cleanup_old_jobs
from app.core.logging import logger

# Import tasks to register them
__all__ = ["celery_app", "process_edit_instruction", "cleanup_old_jobs"]

logger.info("Celery worker initialized")
