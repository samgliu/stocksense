import os
import uuid
import pandas as pd
import math
from sqlalchemy import create_engine, MetaData
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger("stocksense")

def load_companies_into_postgres():
    # Load CSV
    csv_path = "/opt/airflow/data/sp500/sp500_companies.csv"
    df = pd.read_csv(csv_path)

    # Rename columns to match schema
    df = df.rename(
        columns={
            "Symbol": "ticker",
            "Longname": "name",
            "Shortname": "shortname",
            "Exchange": "exchange",
            "Sector": "sector",
            "Industry": "industry",
            "Currentprice": "current_price",
            "Marketcap": "market_cap",
            "Ebitda": "ebitda",
            "Revenuegrowth": "revenue_growth",
            "Fulltimeemployees": "fulltime_employees",
            "Longbusinesssummary": "summary",
        }
    )

    # Generate deterministic UUID using ticker + exchange
    UUID_NAMESPACE = os.environ.get("UUID_NAMESPACE")
    if not UUID_NAMESPACE:
        raise RuntimeError("UUID_NAMESPACE is not set in environment")
    NAMESPACE = uuid.UUID(UUID_NAMESPACE)

    def generate_stable_uuid(ticker: str, exchange: str) -> str:
        key = f"{ticker.upper()}_{exchange.upper()}"
        return str(uuid.uuid5(NAMESPACE, key))

    df["id"] = df.apply(
        lambda row: generate_stable_uuid(row["ticker"], row["exchange"]), axis=1
    )

    df["country"] = "USA"
    if "website" not in df.columns:
        df["website"] = None

    # Drop incomplete and duplicate records
    df = df.dropna(subset=["ticker", "name", "exchange"])
    df = df.drop_duplicates(subset=["id"])
    df = df.where(pd.notnull(df), None)

    # Convert values to Decimal safely
    def safe_decimal(value):
        try:
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return None
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    numeric_columns = [
        "current_price",
        "market_cap",
        "ebitda",
        "revenue_growth",
        "fulltime_employees",
    ]
    for col in numeric_columns:
        df[col] = df[col].apply(safe_decimal)

    # Define the target columns
    columns = [
        "id",
        "ticker",
        "name",
        "shortname",
        "exchange",
        "sector",
        "industry",
        "country",
        "website",
        "summary",
        "current_price",
        "market_cap",
        "ebitda",
        "revenue_growth",
        "fulltime_employees",
    ]

    # Connect to database
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)

    # Reflect the existing "companies" table
    metadata = MetaData()
    metadata.reflect(bind=engine)
    companies_table = metadata.tables["companies"]

    # Use SQLAlchemy session for UPSERT
    with Session(engine) as session:
        for _, row in df.iterrows():
            data = {col: row[col] for col in columns}
            stmt = (
                insert(companies_table)
                .values(**data)
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={col: data[col] for col in columns if col != "id"},
                )
            )
            session.execute(stmt)
        session.commit()

    logger.info(f"✅ Upserted {len(df)} companies into Postgres without duplication.")
