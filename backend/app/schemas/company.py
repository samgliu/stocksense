from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    ticker: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    summary: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
