from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class StockRequest(BaseModel):
    text: str


class StockResponse(BaseModel):
    summary: str


class StockHistoryItem(BaseModel):
    id: UUID
    summary: str
    created_at: datetime
    source_type: Optional[str]
    model_used: Optional[str]
    text_input: Optional[str]

    class Config:
        from_attributes = True
