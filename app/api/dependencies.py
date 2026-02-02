from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.repositories import DocumentRepository, DocumentVersionRepository, JobRepository
from app.services import AzureStorageService
from app.core.logging import logger


# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async for session in get_async_db():
        yield session


# Repository dependencies
def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
    """Get document repository"""
    return DocumentRepository(db)


def get_version_repository(db: AsyncSession = Depends(get_db)) -> DocumentVersionRepository:
    """Get version repository"""
    return DocumentVersionRepository(db)


def get_job_repository(db: AsyncSession = Depends(get_db)) -> JobRepository:
    """Get job repository"""
    return JobRepository(db)


# Service dependencies
def get_storage_service() -> AzureStorageService:
    """Get storage service"""
    return AzureStorageService()


# User ID extraction (placeholder - will be replaced with auth later)
async def get_current_user_id() -> str:
    """
    Get current user ID
    TODO: Replace with actual authentication logic
    """
    # For now, return a test user ID
    # In production, this would extract user from JWT token
    return "test_user_001"
