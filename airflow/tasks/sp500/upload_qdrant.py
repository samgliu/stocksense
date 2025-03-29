import os
import json
import requests


def upload_to_qdrant():
    qdrant_url = os.environ["QDRANT_CLOUD_URL"]
    api_key = os.environ["QDRANT_API_KEY"]
    collection_name = "sp500"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    print("🔍 Loading embedded company records...")
    with open("/opt/airflow/data/sp500/embedded_companies.json") as f:
        records = json.load(f)

    if not records:
        print("❌ No records found in embedded_companies.json")
        return

    print(f"📦 Preparing {len(records)} records for Qdrant...")

    points = []
    for rec in records:
        if "embedding" not in rec or "id" not in rec:
            print(f"⚠️ Skipping invalid record: {rec}")
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

    # Create the collection if it doesn't exist
    vector_size = len(points[0]["vector"])  # dynamic vector size
    collection_config = {
        "vectors": {
            "size": vector_size,
            "distance": "Cosine",
        }
    }

    print(f"🛠 Creating collection `{collection_name}` in Qdrant...")
    response = requests.put(
        f"{qdrant_url}/collections/{collection_name}",
        json=collection_config,
        headers=headers,
    )
    if not response.ok:
        print(f"❌ Failed to create collection: {response.text}")
        return

    print(f"🚀 Uploading {len(points)} points to Qdrant...")
    response = requests.put(
        f"{qdrant_url}/collections/{collection_name}/points?wait=true",
        json={"points": points},
        headers=headers,
    )
    if not response.ok:
        print(f"❌ Failed to upload points: {response.text}")
        return

    print(
        f"✅ Uploaded {len(points)} companies to Qdrant Cloud collection: {collection_name}"
    )
