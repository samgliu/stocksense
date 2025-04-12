import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
import os
from sqlalchemy import create_engine, text


def generate_embeddings():
    print("Loading companies from Postgres...")
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT id, name, ticker, shortname, exchange, industry, sector, country,
                       current_price, market_cap, ebitda, revenue_growth, summary, website, fulltime_employees, insights
                FROM companies
            """
            )
        )
        rows = result.fetchall()
        columns = result.keys()

    print(f"Fetched {len(rows)} companies")

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    records = []
    for row in rows:
        record = dict(zip(columns, row))
        id = str(record["id"])

        # Build text for embedding
        text_input = " ".join(
            filter(
                None,
                [
                    str(record.get("name")),
                    str(record.get("exchange")),
                    str(record.get("ticker")),
                    str(record.get("industry")),
                    str(record.get("sector")),
                    str(record.get("website")),
                    str(record.get("country")),
                    str(record.get("summary")),
                    str(record.get("insights")),
                ],
            )
        )

        embedding = model.encode(text_input, show_progress_bar=False).tolist()

        payload = {k: v for k, v in record.items() if k != "id"}  # all other metadata

        records.append({"id": id, "embedding": embedding, **payload})

    print("Saving enriched embeddings to JSON...")
    os.makedirs("/opt/airflow/data/sp500", exist_ok=True)
    df = pd.DataFrame(records)
    df.to_json("/opt/airflow/data/sp500/embedded_companies.json", orient="records")
    print("✅ Embeddings generated and saved.")
