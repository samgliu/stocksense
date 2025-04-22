import logging
import os
import subprocess
import time

from app.database import Base
from sqlalchemy import create_engine, inspect

logger = logging.getLogger("stocksense")


def wait_for_db(max_attempts=10, delay=3):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
    engine = create_engine(db_url)

    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect():
                logger.info("✅ Database is ready.")
                return engine
        except Exception:
            logger.info(f"⏳ Waiting for DB... ({attempt})")
            time.sleep(delay)

    raise RuntimeError("❌ Database not ready after several attempts.")


def db_needs_migration(engine):
    inspector = inspect(engine)
    return "alembic_version" not in inspector.get_table_names()


import logging

logger = logging.getLogger("stocksense")


def main():
    logger.info("🔍 Checking database status...")
    try:
        engine = wait_for_db()

        if db_needs_migration(engine):
            logger.info("⚠️ No alembic_version table found. Creating tables from SQLAlchemy models...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Tables created.")
        else:
            logger.info("⚙️ Running Alembic migrations...")
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            logger.info("✅ Alembic migration complete.")
    except Exception as e:
        logger.error(f"❌ Migration or DB check failed: {e}")
        return

    logger.info("🚀 Starting FastAPI server...")
    port = os.environ.get("PORT", "8000")
    reload_flag = os.getenv("ENV", "production") == "local"

    uvicorn_cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port]
    if reload_flag:
        uvicorn_cmd.append("--reload")

    subprocess.run(uvicorn_cmd)


if __name__ == "__main__":
    main()
