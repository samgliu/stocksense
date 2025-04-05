# app/schemas/news.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class NewsBase(BaseModel):
    title: str
    description: Optional[str] = None
    snippet: Optional[str] = None
    url: HttpUrl
    image_url: Optional[HttpUrl] = None
    published_at: datetime
    source: Optional[str] = None
    language: Optional[str] = None
    categories: Optional[List[str]] = None
    relevance_score: Optional[str] = None
    company_id: UUID

    class Config:
        from_attributes = True


class NewsResponse(NewsBase):
    id: UUID
