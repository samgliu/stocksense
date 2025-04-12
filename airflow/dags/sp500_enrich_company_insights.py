from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from tasks.sp500.pull_from_db import pull_unenriched_companies
from tasks.sp500.insights_enrich import enrich_companies_from_csv
from tasks.sp500.embed import generate_embeddings
from tasks.sp500.upload_qdrant import upload_to_qdrant
from tasks.sp500.import_insights_to_db import import_insights_from_csv

with DAG(
    dag_id="enrich_company_insights",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["ai", "ollama", "enrichment"],
) as dag:

    pull = PythonOperator(
        task_id="pull_unenriched_companies",
        python_callable=pull_unenriched_companies,
    )

    enrich = PythonOperator(
        task_id="enrich_insights",
        python_callable=enrich_companies_from_csv,
    )

    import_insights = PythonOperator(
        task_id="import_enriched_to_postgres",
        python_callable=import_insights_from_csv,
    )

    embed = PythonOperator(
        task_id="embed_enriched_companies",
        python_callable=generate_embeddings,
    )

    upload = PythonOperator(
        task_id="upload_enriched_to_qdrant",
        python_callable=upload_to_qdrant,
    )

    pull >> enrich >> import_insights >> embed >> upload
