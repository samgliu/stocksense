import os
import json
import requests
import logging

logger = logging.getLogger("stocksense")


def upload_to_qdrant():
    qdrant_url = os.environ["QDRANT_CLOUD_URL"]
    api_key = os.environ["QDRANT_API_KEY"]
    collection_name = "sp500"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    logger.info("🔍 Loading embedded company records...")
    with open("/opt/airflow/data/sp500/embedded_companies.json") as f:
        records = json.load(f)

    if not records:
        logger.error("❌ No records found in embedded_companies.json")
        return

    logger.info(f"📦 Preparing {len(records)} records for Qdrant...")

    points = []
    for rec in records:
        if "embedding" not in rec or "id" not in rec:
            logger.info(f"⚠️ Skipping invalid record: {rec}")
            continue

        payload = {
            k: v
            for k, v in rec.items()
            if k not in ("id", "embedding") and v is not None
        }

        points.append(
            {
                "id": rec["id"],
                "vector": rec["embedding"],
                "payload": payload,
            }
        )

    # Check if collection exists
    logger.info(f"🔎 Checking if collection `{collection_name}` exists...")
    exists_response = requests.get(
        f"{qdrant_url}/collections/{collection_name}",
        headers=headers,
    )

    if exists_response.status_code == 200:
        logger.info(f"✅ Collection `{collection_name}` already exists, skipping creation.")
    else:
        logger.info(f"🛠 Creating collection `{collection_name}` in Qdrant...")
        vector_size = len(points[0]["vector"])
        collection_config = {
            "vectors": {"size": vector_size, "distance": "Cosine"},
        }
        create_response = requests.put(
            f"{qdrant_url}/collections/{collection_name}",
            json=collection_config,
            headers=headers,
        )
        if not create_response.ok:
            logger.info(f"❌ Failed to create collection: {create_response.text}")
            return

    # Upsert points (update or insert)
    logger.info(f"🚀 Uploading {len(points)} points to Qdrant via UPSERT...")
    upsert_response = requests.put(
        f"{qdrant_url}/collections/{collection_name}/points?wait=true",
        json={"points": points},
        headers=headers,
    )
    if not upsert_response.ok:
        logger.info(f"❌ Failed to upload points: {upsert_response.text}")
        return

    logger.info(
        f"✅ Uploaded {len(points)} companies to Qdrant Cloud collection: {collection_name}"
    )
