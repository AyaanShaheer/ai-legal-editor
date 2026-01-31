from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.database import Base
from app.core.logging import logger

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Async session maker
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sync engine for Celery workers
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Sync session maker
sync_session_maker = sessionmaker(
    sync_engine,
    class_=Session,
    expire_on_commit=False
)


async def get_async_db():
    """Dependency for FastAPI routes to get async DB session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """Function for Celery workers to get sync DB session"""
    db = sync_session_maker()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def create_tables():
    """Create all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def drop_tables():
    """Drop all database tables (use with caution!)"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped")
