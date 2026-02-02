from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.database import Base
from app.core.logging import logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record
        
        Args:
            **kwargs: Model fields
            
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        logger.info(f"Created {self.model.__name__} with id={instance.id}")
        return instance
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get record by ID
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        instance = result.scalar_one_or_none()
        return instance
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of model instances
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        instances = result.scalars().all()
        return list(instances)
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Update record by ID
        
        Args:
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None
        """
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.db.flush()
        
        updated = await self.get_by_id(id)
        if updated:
            logger.info(f"Updated {self.model.__name__} id={id}")
        return updated
    
    async def delete(self, id: int) -> bool:
        """
        Delete record by ID
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        deleted = result.rowcount > 0
        
        if deleted:
            logger.info(f"Deleted {self.model.__name__} id={id}")
        
        return deleted
    
    async def count(self) -> int:
        """
        Count total records
        
        Returns:
            Total count
        """
        result = await self.db.execute(
            select(self.model)
        )
        return len(result.scalars().all())
