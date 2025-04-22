import os
import requests
from datetime import datetime
import logging

logger = logging.getLogger("stocksense")

def download_sp500_zip():
    url = "https://www.kaggle.com/api/v1/datasets/download/andrewmvd/sp-500-stocks"
    output_path = "/opt/airflow/data/sp500.zip"

    if os.path.exists(output_path):
        modified_time = datetime.fromtimestamp(os.path.getmtime(output_path))
        now = datetime.now()
        if modified_time.date() == now.date():
            logger.info("✅ SP500 zip is up-to-date (downloaded today). Skipping download.")
            return
        else:
            logger.info("🔁 SP500 zip exists but is outdated. Re-downloading...")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    with open(output_path, "wb") as f:
        f.write(response.content)
    logger.info("📦 Downloaded SP500 zip")
