import os
import backoff
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from asyncpg import exceptions

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, future=True, echo=True)

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
async def get_async_db():
    """Async database connection with retry logic"""
    async with AsyncSessionLocal() as session:
        return session
