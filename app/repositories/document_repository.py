from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.database import Document, DocumentVersion
from app.repositories.base import BaseRepository
from app.core.logging import logger


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Document, db)
    
    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        Get all documents for a specific user
        
        Args:
            user_id: User ID
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of documents
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .options(selectinload(Document.versions))
            .offset(skip)
            .limit(limit)
            .order_by(Document.created_at.desc())
        )
        documents = result.scalars().all()
        logger.info(f"Retrieved {len(documents)} documents for user {user_id}")
        return list(documents)
    
    async def get_by_id_with_versions(self, document_id: int) -> Optional[Document]:
        """
        Get document with all versions loaded
        
        Args:
            document_id: Document ID
            
        Returns:
            Document with versions or None
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.versions))
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_with_jobs(self, document_id: int) -> Optional[Document]:
        """
        Get document with all jobs loaded
        
        Args:
            document_id: Document ID
            
        Returns:
            Document with jobs or None
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.jobs))
        )
        return result.scalar_one_or_none()
    
    async def count_by_user(self, user_id: str) -> int:
        """
        Count documents for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Document count
        """
        result = await self.db.execute(
            select(Document).where(Document.user_id == user_id)
        )
        return len(result.scalars().all())
    
    async def search_by_filename(
        self, 
        user_id: str, 
        filename_query: str
    ) -> List[Document]:
        """
        Search documents by filename
        
        Args:
            user_id: User ID
            filename_query: Filename search query
            
        Returns:
            List of matching documents
        """
        result = await self.db.execute(
            select(Document)
            .where(
                Document.user_id == user_id,
                Document.original_filename.ilike(f"%{filename_query}%")
            )
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())
