import os
import pandas as pd
from sqlalchemy import create_engine, MetaData, update

CSV_PATH = "/opt/airflow/data/sp500/enriched_companies.csv"


def import_insights_from_csv():
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    print("📦 Available tables:", list(metadata.tables.keys()))

    table_name = "companies"
    if table_name not in metadata.tables:
        raise ValueError(f"❌ Table '{table_name}' not found in database.")

    companies = metadata.tables[table_name]

    df = pd.read_csv(CSV_PATH)
    print(f"📥 Importing insights for {len(df)} companies")

    with engine.begin() as conn:
        for _, row in df.iterrows():
            if not row.get("insight"):
                print(f"⚠️ Skipping {row['ticker']} — no insight")
                continue

            stmt = (
                update(companies)
                .where(companies.c.id == row["id"])
                .values(insights=row["insight"])
            )
            conn.execute(stmt)
            print(f"✅ Updated: {row['ticker']}")

    print(f"🎉 All insights imported successfully.")
