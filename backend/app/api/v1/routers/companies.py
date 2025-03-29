from fastapi import APIRouter, HTTPException, Depends
from app.services.fmp import fetch_company_profile_async
from pydantic import BaseModel
from app.models import Company
from app.database import get_async_db
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class CompanyProfileOut(BaseModel):
    symbol: str
    companyName: str
    price: Optional[float]
    website: Optional[str]
    industry: Optional[str]
    sector: Optional[str]
    description: Optional[str]
    ceo: Optional[str]
    country: Optional[str]
    city: Optional[str]
    state: Optional[str]
    fullTimeEmployees: Optional[int]
    image: Optional[str]
    ipoDate: Optional[str]


@router.get("/{uuid}/{ticker}")
async def get_company_profile(
    uuid: str, ticker: str, db: AsyncSession = Depends(get_async_db)
):
    # 1. Try FMP
    profile = await fetch_company_profile_async(ticker)
    if profile:
        return profile

    # 2. Fallback to DB
    try:
        stmt = select(Company).where(Company.ticker == ticker.upper())
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        if company:
            return company
    except Exception as e:
        print(f"❌ DB fallback failed for {ticker}: {e}")

    raise HTTPException(status_code=404, detail="Company not found")
