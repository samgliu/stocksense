from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from typing import Optional, List
import os
import httpx
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

router = APIRouter()

QDRANT_URL = os.environ["QDRANT_CLOUD_URL"]
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
executor = ThreadPoolExecutor(max_workers=2)


class SemanticResult(BaseModel):
    id: str
    name: str
    ticker: str
    summary: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    domain: Optional[str] = None
    score: float


@router.get("/semantic-search", response_model=List[SemanticResult])
async def semantic_search(
    request: Request, query: str = Query(..., min_length=3), top_k: int = 10
):
    # Run embedding in a background thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    vector = await loop.run_in_executor(executor, model.encode, query)
    vector = vector.tolist()

    # Use async client to call Qdrant
    async with httpx.AsyncClient() as client:
        response = await client.post(
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
            sector=r["payload"].get("sector"),
            industry=r["payload"].get("industry"),
            domain=r["payload"].get("domain"),
            score=r["score"],
        )
        for r in results
    ]
