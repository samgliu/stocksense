from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict
from datetime import datetime


class AnalysisReportSchema(BaseModel):
    id: UUID
    stock_entry_id: UUID
    model_version: Optional[str] = None

    current_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None
    time_horizon: Optional[str] = "30d"

    prediction_json: Dict
    insights: Optional[str] = None
    summary: Optional[str] = None

    created_at: datetime

    class Config:
        orm_mode = True


class AnalysisReportResponse(BaseModel):
    id: UUID
    stock_entry_id: UUID
    current_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None
    time_horizon: Optional[str] = "30d"
    summary: Optional[str] = None
    insights: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
