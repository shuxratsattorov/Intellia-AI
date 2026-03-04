import os
import sys
from fastapi import Depends
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy import func, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app.core.config  import settings
from app.db.factory import get_async_factory


async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False
)
async_session = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


async def create_async_session(factory = Depends(get_async_factory)):
    async with factory() as session:
        yield session


@asynccontextmanager
async def get_async_session():
    async with async_session() as session:
        async with session.begin():
            yield session
