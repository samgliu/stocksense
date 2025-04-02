from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime


class AnalysisReportBase(BaseModel):
    company_id: Optional[UUID] = None
    ticker: Optional[str] = None
    exchange: Optional[str] = None
    model_version: Optional[str] = None

    current_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None
    time_horizon: Optional[str] = "30d"

    prediction_json: Dict
    insights: Optional[str] = None
    summary: Optional[str] = None


class AnalysisReportResponse(AnalysisReportBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)