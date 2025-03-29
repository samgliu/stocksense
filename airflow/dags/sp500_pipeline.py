from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

from tasks.sp500.download import download_sp500_zip
from tasks.sp500.extract import extract_csv_from_zip
from tasks.sp500.load_postgres import load_companies_into_postgres
from tasks.sp500.embed import generate_embeddings
from tasks.sp500.upload_qdrant import upload_to_qdrant

with DAG(
    dag_id="sp500_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    tags=["sp500", "pipeline"],
) as dag:

    task_download = PythonOperator(
        task_id="download_sp500_zip",
        python_callable=download_sp500_zip,
    )

    task_extract = PythonOperator(
        task_id="extract_csv",
        python_callable=extract_csv_from_zip,
    )

    task_load_postgres = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_companies_into_postgres,
    )

    task_generate_embeddings = PythonOperator(
        task_id="generate_embeddings",
        python_callable=generate_embeddings,
    )

    task_upload_qdrant = PythonOperator(
        task_id="upload_to_qdrant",
        python_callable=upload_to_qdrant,
    )

    (
        task_download
        >> task_extract
        >> task_load_postgres
        >> task_generate_embeddings
        >> task_upload_qdrant
    )
