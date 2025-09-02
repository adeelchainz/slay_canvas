"""
Database initialization and utility functions
"""
import asyncio
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from app.db.session import async_engine, SessionLocal
from app.models.user import User
from app.models.media import MediaFile
from app.models.transcript import Transcript
import logging

logger = logging.getLogger(__name__)

async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Parse the database URL to get database name
        db_url_parts = settings.DATABASE_URL.split('/')
        db_name = db_url_parts[-1]
        base_url = '/'.join(db_url_parts[:-1])
        
        # Connect to PostgreSQL (not specific database)
        postgres_url = f"{base_url}/postgres"
        engine = create_engine(postgres_url.replace('+asyncpg', ''))
        
        # Check if database exists
        with engine.connect() as conn:
            # Ensure we're not in a transaction
            if conn.in_transaction():
                conn.commit()
            result = conn.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
            )
            exists = result.fetchone() is not None
            
        if not exists:
            # Use autocommit mode for CREATE DATABASE
            engine.execution_options(isolation_level="AUTOCOMMIT")
            with engine.connect() as conn:
                conn.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Created database: {db_name}")
        else:
            print(f"✅ Database {db_name} already exists")
            
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

async def init_database():
    """Initialize database with tables"""
    try:
        # First create database if needed
        await create_database_if_not_exists()
        
        # Import models to ensure they're registered
        from app.models import user, media, transcript
        
        # Create all tables
        async with async_engine.begin() as conn:
            # Import Base from your models
            from app.models.user import Base
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        print(f"❌ Error initializing database: {e}")
        return False

async def check_database_connection():
    """Check if database connection is working"""
    try:
        async with SessionLocal() as session:
            # Try a simple query
            result = await session.execute("SELECT 1")
            result.fetchone()
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_database_sync():
    """Synchronous version for testing"""
    return asyncio.run(check_database_connection())

if __name__ == "__main__":
    # Run initialization
    asyncio.run(init_database())
