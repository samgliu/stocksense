import subprocess
import time
import os
from sqlalchemy import create_engine, inspect
from app.database import Base
from app import models


def wait_for_db(max_attempts=10, delay=3):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
    engine = create_engine(db_url)

    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect():
                print("✅ Database is ready.")
                return engine
        except Exception as e:
            print(f"⏳ Waiting for DB... ({attempt})")
            time.sleep(delay)

    raise RuntimeError("❌ Database not ready after several attempts.")


def db_needs_migration(engine):
    inspector = inspect(engine)
    return "alembic_version" not in inspector.get_table_names()


def main():
    print("🔍 Checking database status...")
    try:
        engine = wait_for_db()

        if db_needs_migration(engine):
            print(
                "⚠️ No alembic_version table found. Creating tables from SQLAlchemy models..."
            )
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created.")
        else:
            print("⚙️ Running Alembic migrations...")
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            print("✅ Alembic migration complete.")
    except Exception as e:
        print(f"❌ Migration or DB check failed: {e}")
        return

    print("🚀 Starting FastAPI server...")
    subprocess.run(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    )


if __name__ == "__main__":
    main()
