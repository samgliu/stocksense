import csv
import requests
from pathlib import Path
import pandas as pd
import re


# Configuration
OLLAMA_URL = "http://192.168.7.225:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"
UNENRICHED_PATH = Path("/opt/airflow/data/sp500/unenriched_companies.csv")
ENRICHED_PATH = Path("/opt/airflow/data/sp500/enriched_companies.csv")

INSIGHT_PROMPT = """You are a financial analyst AI. Based on the structured company profile below, write a long, detailed, and keyword-rich investment insight. Your goal is to provide dense information suitable for AI semantic search embeddings. Include key facts about the company’s sector, industry, business model, market, and strategic strengths.

Company Name: {name}
Sector: {sector}
Industry: {industry}
Country: {country}
Description: {summary}

Write a multi-paragraph insight suitable for machine understanding:
"""


def generate_insight(prompt: str, model: str = MODEL_NAME) -> str:
    res = requests.post(
        OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=60
    )
    res.raise_for_status()
    raw = res.json()["response"].strip()

    # Remove <think>...</think> and similar tags if any
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    return cleaned


def enrich_companies_from_csv(ti=None):
    if not UNENRICHED_PATH.exists():
        raise FileNotFoundError(f"{UNENRICHED_PATH} not found.")

    # Load all unenriched companies
    df_unenriched = pd.read_csv(UNENRICHED_PATH)
    df_enriched = (
        pd.read_csv(ENRICHED_PATH) if ENRICHED_PATH.exists() else pd.DataFrame()
    )

    already_done = (
        set(df_enriched["id"].astype(str)) if not df_enriched.empty else set()
    )
    remaining = df_unenriched[~df_unenriched["id"].astype(str).isin(already_done)]

    print(f"🔁 {len(remaining)} companies to enrich (skipping {len(already_done)})")

    enriched_this_run = []

    # Prepare to append to enriched CSV
    fieldnames = list(df_unenriched.columns) + ["insight"]
    ENRICHED_PATH.parent.mkdir(parents=True, exist_ok=True)
    append_header = not ENRICHED_PATH.exists()

    with open(ENRICHED_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if append_header:
            writer.writeheader()

        for _, row in remaining.iterrows():
            try:
                prompt = INSIGHT_PROMPT.format(
                    name=row["name"],
                    sector=row["sector"],
                    industry=row["industry"],
                    country=row["country"],
                    summary=row["summary"],
                )
                insight = generate_insight(prompt)

                record = row.to_dict()
                record["insight"] = insight
                writer.writerow(record)
                enriched_this_run.append(record)

                print(f"✅ Enriched: {row['ticker']}")

            except Exception as e:
                print(f"❌ {row['ticker']}: {e}")

    print(f"💾 Wrote {len(enriched_this_run)} enriched records to {ENRICHED_PATH}")

    if ti:
        ti.xcom_push(key="enriched_companies", value=enriched_this_run)


# Optional CLI entrypoint
if __name__ == "__main__":
    enrich_companies_from_csv()
