from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CompanyBase(BaseModel):
    ticker: str
    name: str
    exchange: Optional[str] = None
    shortname: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = "USA"
    website: Optional[str] = None
    summary: Optional[str] = None

    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    ebitda: Optional[float] = None
    revenue_growth: Optional[float] = None
    fulltime_employees: Optional[int] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
