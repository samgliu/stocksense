from app.schemas.company_news import NewsBase
import httpx
from typing import List
from datetime import datetime
from uuid import UUID
import os

NEWS_API_TOKEN = os.getenv("THE_NEWS_API_KEY")
NEWS_API_URL = "https://api.thenewsapi.com/v1/news/all"


async def fetch_company_news(company_name: str, company_id: UUID) -> List[NewsBase]:
    params = {
        "api_token": NEWS_API_TOKEN,
        "search": company_name,
        "language": "en",
        "local": "us",
        "limit": 3,
        "sort": "published_at",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        items = response.json().get("data", [])
        return [
            NewsBase(
                title=item["title"],
                description=item.get("description"),
                snippet=item.get("snippet"),
                url=str(item["url"]),
                image_url=str(item.get("image_url")) if item.get("image_url") else None,
                published_at=datetime.fromisoformat(
                    item["published_at"].replace("Z", "+00:00")
                ),
                source=item.get("source"),
                language=item.get("language"),
                categories=item.get("categories", []),
                relevance_score=str(item.get("relevance_score")),
                company_id=company_id,
            )
            for item in items
        ]
