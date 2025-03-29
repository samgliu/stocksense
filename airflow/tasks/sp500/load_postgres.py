import pandas as pd
import uuid
from sqlalchemy import create_engine
import os


def load_companies_into_postgres():
    csv_path = "/opt/airflow/data/sp500/sp500_companies.csv"
    df = pd.read_csv(csv_path)

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
        }
    )

    # Add required fields
    df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    df["country"] = "USA"
    df["website"] = None
    df["summary"] = None

    # Drop incomplete records
    df = df.dropna(subset=["ticker", "name"])
    df = df.drop_duplicates(subset=["ticker"])

    # Match DB schema (excluding created_at which is server default)
    df = df[
        [
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
    ]

    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    df.to_sql("companies", engine, if_exists="replace", index=False)

    print("✅ Loaded enriched companies into Postgres")
