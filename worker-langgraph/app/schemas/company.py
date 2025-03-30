from pydantic import BaseModel
from typing import List, Optional
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


class HistoryPoint(BaseModel):
    date: str
    close: float


class CompanyPayload(BaseModel):
    id: str
    ticker: str
    name: str
    shortname: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
    ceo: Optional[str] = None
    ipo_date: Optional[str] = None
    image: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    ebitda: Optional[float] = None
    revenue_growth: Optional[float] = None
    vol_avg: Optional[int] = None
    beta: Optional[float] = None
    last_dividend: Optional[float] = None
    range_52w: Optional[str] = None
    dcf: Optional[float] = None
    dcf_diff: Optional[float] = None
    currency: Optional[str] = None
    is_etf: Optional[bool] = None
    is_adr: Optional[bool] = None
    is_fund: Optional[bool] = None
    is_actively_trading: Optional[bool] = None
    fulltime_employees: Optional[int] = None


class AnalyzeRequest(BaseModel):
    company: CompanyPayload
    history: Optional[List[HistoryPoint]] = None