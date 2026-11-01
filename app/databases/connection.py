from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from app.core.config import settings


# Create database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)


# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Provide database session to FastAPI routes
async def get_db():

    async with AsyncSessionLocal() as session:
        yield session