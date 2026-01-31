import asyncio
from app.core.database import create_tables, drop_tables
from app.core.logging import logger


async def init_database():
    """Initialize database with tables"""
    logger.info("Initializing database...")
    await create_tables()
    logger.info("Database initialization complete!")


async def reset_database():
    """Reset database (drop and recreate tables)"""
    logger.info("Resetting database...")
    await drop_tables()
    await create_tables()
    logger.info("Database reset complete!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        asyncio.run(reset_database())
    else:
        asyncio.run(init_database())
