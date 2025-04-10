import os
from typing import AsyncGenerator
import backoff
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base
from asyncpg import exceptions

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_size=30,
    max_overflow=50,
    pool_timeout=60,
    pool_recycle=600,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False, autocommit=False
)

Base = declarative_base()


@backoff.on_exception(
    backoff.expo,
    exceptions.TooManyConnectionsError,
    max_tries=5,
    jitter=backoff.full_jitter,
)
async def _get_session() -> AsyncSession:
    return AsyncSessionLocal()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    session = await _get_session()
    try:
        yield session
    finally:
        await session.close()
