import os
import sys
from fastapi import Depends
from app.core.config  import settings
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, async_sessionmaker
)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


async_session_factory: async_sessionmaker | None = None

def get_async_factory() -> async_sessionmaker:
    return async_session_factory


async_engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker[AsyncSession](
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session


async def create_async_session(factory = Depends(get_async_factory)):
    async with factory() as session:
        yield session
