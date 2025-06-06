import zipfile
import logging

logger = logging.getLogger("stocksense")

def extract_csv_from_zip():
    zip_path = "/opt/airflow/data/sp500.zip"
    extract_path = "/opt/airflow/data/sp500"
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    logger.info("Extracted CSV from ZIP")
