from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from app.models.analysis_report import AnalysisReport
from app.schemas.analysis_report import AnalysisReportResponse
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import Company
from app.models.stock_entry import StockEntry
from app.models.usage_log import UsageLog
from app.models.user import User, UserRole
from app.models import JobStatus
from app.services.fmp import fetch_company_profile_async
from app.services.yf_data import fetch_historical_prices
from app.services.company_analysis import analyze_company_payload
from app.core.config import USER_DAILY_LIMIT
from app.kafka.producer import send_analysis_job

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


@router.get("/profile/{uuid}/{ticker}")
async def get_company_profile(
    request: Request, uuid: str, ticker: str, db: AsyncSession = Depends(get_async_db)
):
    profile = await fetch_company_profile_async(ticker)
    if profile:
        return profile

    try:
        stmt = select(Company).where(Company.id == uuid)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        if company:
            return company
    except Exception as e:
        print(f"❌ DB fallback failed for {ticker}: {e}")

    raise HTTPException(status_code=404, detail="Company not found")


@router.get("/historical/{exchange}/{ticker}")
async def get_historical_prices(request: Request, exchange: str, ticker: str):
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
    company_id: str
    company: CompanyPayload
    history: Optional[List[HistoryPoint]] = None


@router.post("/analyze")
async def analyze_company(
    request: Request,
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_async_db),
):
    user_data = request.state.user
    user_result = await db.execute(select(User).where(User.email == user_data["email"]))
    user = user_result.scalar_one()

    if user.role == UserRole.USER:
        start_of_day = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        usage_result = await db.execute(
            select(func.count())
            .select_from(UsageLog)
            .where(UsageLog.user_id == user.id, UsageLog.created_at >= start_of_day)
        )
        usage_count_today = usage_result.scalar()
        if usage_count_today >= USER_DAILY_LIMIT:
            raise HTTPException(status_code=429, detail="Daily usage limit reached")

    job_id = str(uuid4())
    send_analysis_job(
        {
            "job_id": job_id,
            "user_id": str(user.id),
            "email": user.email,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "body": body.dict(),
        }
    )
    db.add(
        JobStatus(
            job_id=job_id,
            user_id=user.id,
            status="queued",
            input=body.json(),
        )
    )
    db.add(UsageLog(user_id=user.id, action="analyze"))
    await db.commit()

    return {"status": "queued", "job_id": job_id}


@router.get(
    "/analysis-reports/{company_id}",
    response_model=List[AnalysisReportResponse],
)
async def get_reports_for_company(
    company_id: UUID, db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(AnalysisReport)
        .where(AnalysisReport.company_id == company_id)
        .order_by(AnalysisReport.created_at.asc())
    )
    reports = result.scalars().all()
    print(reports)
    print(type(reports))
    return reports
