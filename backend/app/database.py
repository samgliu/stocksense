import os
from typing import AsyncGenerator

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_size=10,
    max_overflow=5,
    pool_timeout=60,
    pool_recycle=600,
    pool_pre_ping=True,
)
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT")
if OTLP_ENDPOINT:
    SQLAlchemyInstrumentor().instrument(
        engine=engine.sync_engine,
    )
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)

Base = declarative_base()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
