import os
import pandas as pd
from sqlalchemy import create_engine, MetaData, update
import logging

logger = logging.getLogger("stocksense")

CSV_PATH = "/opt/airflow/data/sp500/enriched_companies.csv"


def import_insights_from_csv():
    db_url = os.environ["DATABASE_URL"]

    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    logger.info(f"\ud83d\udce6 Available tables: {list(metadata.tables.keys())}")

    table_name = "companies"
    if table_name not in metadata.tables:
        raise ValueError(f"❌ Table '{table_name}' not found in database.")

    companies = metadata.tables[table_name]

    df = pd.read_csv(CSV_PATH)
    logger.info(f"\ud83d\udce5 Importing insights for {len(df)} companies")

    with engine.begin() as conn:
        for _, row in df.iterrows():
            if not row.get("insight"):
                logger.warning(f"\u26a0\uFE0F Skipping {row['ticker']} — no insight")
                continue

            stmt = (
                update(companies)
                .where(companies.c.id == row["id"])
                .values(insights=row["insight"])
            )
            conn.execute(stmt)
            logger.info(f"✅ Updated: {row['ticker']}")

    logger.info("🎉 All insights imported successfully.")
