from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import requests
import os
from sentence_transformers import SentenceTransformer

router = APIRouter()

QDRANT_URL = os.environ["QDRANT_CLOUD_URL"]
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class SemanticResult(BaseModel):
    id: str
    name: str
    ticker: str
    summary: Optional[str] = None
    score: float


@router.get("/semantic-search", response_model=list[SemanticResult])
def semantic_search(query: str = Query(..., min_length=3), top_k: int = 10):
    vector = model.encode(query).tolist()

    response = requests.post(
        f"{QDRANT_URL}/collections/sp500/points/search",
        headers={"api-key": QDRANT_API_KEY, "Content-Type": "application/json"},
        json={
            "vector": vector,
            "top": top_k,
            "with_payload": True,
        },
    )
    response.raise_for_status()
    results = response.json()["result"]

    return [
        SemanticResult(
            id=r["id"],
            name=r["payload"].get("name"),
            ticker=r["payload"].get("ticker"),
            summary=r["payload"].get("summary"),
            score=r["score"],
        )
        for r in results
    ]
