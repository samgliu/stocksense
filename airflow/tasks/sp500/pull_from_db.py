import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, MetaData, select

UNENRICHED_PATH = Path("/opt/airflow/data/sp500/unenriched_companies.csv")
DAYS_VALID = 7


def pull_unenriched_companies():
    if UNENRICHED_PATH.exists():
        last_modified = datetime.fromtimestamp(UNENRICHED_PATH.stat().st_mtime)
        age_days = (datetime.now() - last_modified).days
        if age_days < DAYS_VALID:
            print(
                f"⏩ Skipped pulling — CSV already exists and is {age_days} day(s) old (valid for {DAYS_VALID} days)"
            )
            return

    db_url = os.environ["DATABASE_URL"]

    engine = create_engine(
        db_url,
        pool_size=1,
        max_overflow=0,
        pool_timeout=30,
        pool_recycle=1800,
    )

    metadata = MetaData()
    metadata.reflect(bind=engine)
    companies = metadata.tables["companies"]

    with engine.connect() as conn:
        result = conn.execute(
            select(
                companies.c.id,
                companies.c.name,
                companies.c.ticker,
                companies.c.sector,
                companies.c.industry,
                companies.c.country,
                companies.c.summary,
            )
        )
        rows = result.fetchall()

    records = [
        {
            "id": str(r.id),
            "name": r.name,
            "ticker": r.ticker,
            "sector": r.sector or "",
            "industry": r.industry or "",
            "country": r.country or "USA",
            "summary": r.summary or "",
        }
        for r in rows
    ]

    UNENRICHED_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(UNENRICHED_PATH, index=False)
    print(f"📥 Pulled {len(records)} rows to {UNENRICHED_PATH}")
