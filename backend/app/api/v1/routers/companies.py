from app.services.yf_data import fetch_historical_prices
from app.services.company_analysis import analyze_company_payload
from fastapi import APIRouter, HTTPException, Depends
from app.services.fmp import fetch_company_profile_async
from pydantic import BaseModel
from app.models import Company
from app.database import get_async_db
from typing import Optional, List
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


@router.get("/historical/{exchange}/{ticker}")
async def get_historical_prices(exchange: str, ticker: str):
    try:
        full_ticker = f"{ticker}.{exchange}" if exchange.upper() != "NASDAQ" else ticker
        prices = await fetch_historical_prices(full_ticker)
        if not prices:
            raise HTTPException(status_code=404, detail="No historical data found")
        return prices
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")


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
    history: List[HistoryPoint]


@router.post("/analyze")
async def analyze_company(request: AnalyzeRequest):
    try:
        result = await analyze_company_payload(request.dict())
        return {"analysis": result}
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return {"error": "Failed to analyze company"}
