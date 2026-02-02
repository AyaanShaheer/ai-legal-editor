from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.database import DocumentVersion
from app.repositories.base import BaseRepository
from app.core.logging import logger


class DocumentVersionRepository(BaseRepository[DocumentVersion]):
    """Repository for DocumentVersion model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DocumentVersion, db)
    
    async def get_by_document(self, document_id: int) -> List[DocumentVersion]:
        """
        Get all versions for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of versions ordered by version number
        """
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.asc())
        )
        versions = result.scalars().all()
        logger.info(f"Retrieved {len(versions)} versions for document {document_id}")
        return list(versions)
    
    async def get_latest_version(self, document_id: int) -> Optional[DocumentVersion]:
        """
        Get the latest version of a document
        
        Args:
            document_id: Document ID
            
        Returns:
            Latest version or None
        """
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_version_by_number(
        self, 
        document_id: int, 
        version_number: int
    ) -> Optional[DocumentVersion]:
        """
        Get specific version by number
        
        Args:
            document_id: Document ID
            version_number: Version number
            
        Returns:
            Version or None
        """
        result = await self.db.execute(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version_number
            )
        )
        return result.scalar_one_or_none()
    
    async def get_next_version_number(self, document_id: int) -> int:
        """
        Get the next version number for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            Next version number
        """
        latest = await self.get_latest_version(document_id)
        return (latest.version_number + 1) if latest else 1
    
    async def count_by_document(self, document_id: int) -> int:
        """
        Count versions for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            Version count
        """
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
        )
        return len(result.scalars().all())
