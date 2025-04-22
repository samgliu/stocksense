import json
import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from app.core.config import USER_DAILY_LIMIT
from app.database import get_async_db
from app.kafka.producer import send_analysis_job
from app.models import Company, JobStatus
from app.models.analysis_report import AnalysisReport
from app.models.company_news import CompanyNews
from app.models.usage_log import UsageLog
from app.models.user import User, UserRole
from app.schemas.analysis_report import AnalysisReportResponse
from app.schemas.company_news import NewsResponse
from app.services.fmp import fetch_company_profile_async
from app.services.news import fetch_company_news
from app.services.redis import redis_client
from app.services.yf_data import fetch_historical_prices
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("stocksense")

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
async def get_company_profile(request: Request, uuid: str, ticker: str, db: AsyncSession = Depends(get_async_db)):
    cache_key = f"company:profile:{uuid}:{ticker}"

    # Try Redis cache first
    cached = await redis_client.get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except Exception as e:
            logger.error(f"Failed to parse Redis cache for {cache_key}: {e}")

    # Try fetching from external FMP API
    profile = await fetch_company_profile_async(ticker)

    if profile:
        try:
            # Try to fetch insights from your database
            stmt = select(Company).where(Company.id == uuid)
            result = await db.execute(stmt)
            company = result.scalar_one_or_none()

            if company and company.insights:
                profile["insights"] = company.insights

        except Exception as e:
            logger.error(f"Failed to fetch insights for {uuid}: {e}")

        # Cache the combined profile
        await redis_client.set(cache_key, json.dumps(profile), ex=60 * 60 * 6)
        return profile

    # Fallback to local database if FMP call fails
    try:
        stmt = select(Company).where(Company.id == uuid)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        if company:
            company_dict = (
                company.to_dict()
                if hasattr(company, "to_dict")
                else json.loads(json.dumps(company.__dict__, default=str))
            )
            await redis_client.set(cache_key, json.dumps(company_dict), ex=60 * 60 * 6)
            return company_dict
    except Exception as e:
        logger.error(f"DB fallback failed for {ticker}: {e}")

    raise HTTPException(status_code=404, detail="Company not found")


@router.get("/historical/{exchange}/{ticker}")
async def get_historical_prices(request: Request, exchange: str, ticker: str):
    full_ticker = f"{ticker}.{exchange}" if exchange.upper() != "NASDAQ" else ticker
    cache_key = f"stock:historical:{full_ticker}"

    # Try Redis first
    cached = await redis_client.get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except Exception as e:
            logger.error(f"⚠️ Redis parse failed for {cache_key}: {e}")

    # Fetch from external source
    prices = await fetch_historical_prices(full_ticker)
    if not prices:
        raise HTTPException(status_code=404, detail="No historical data found")

    await redis_client.set(cache_key, json.dumps(prices), ex=60 * 60 * 6)  # 6 hours TTL
    return prices


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


class NewsSnippet(BaseModel):
    title: str
    snippet: Optional[str] = None
    published_at: datetime


class AnalyzeRequest(BaseModel):
    company_id: str
    company: CompanyPayload
    insights: Optional[str] = None
    history: Optional[List[HistoryPoint]] = None
    news: Optional[List[NewsSnippet]] = None


@router.post("/analyze")
async def analyze_company(
    request: Request,
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_async_db),
):
    user_data = request.state.user
    user_result = await db.execute(select(User).where(User.firebase_uid == user_data["uid"]))
    user = user_result.scalar_one()

    if user.role != UserRole.ADMIN:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        usage_result = await db.execute(
            select(func.count())
            .select_from(UsageLog)
            .where(UsageLog.user_id == user.id, UsageLog.created_at >= start_of_day)
        )
        usage_count_today = usage_result.scalar()
        if usage_count_today >= USER_DAILY_LIMIT:
            raise HTTPException(status_code=429, detail="Daily usage limit reached")

    job_id = str(uuid4())
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
    await send_analysis_job(
        {
            "job_id": job_id,
            "user_id": str(user.id),
            "email": user.email,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "body": body.model_dump(mode="json"),
        }
    )
    await redis_client.set(
        f"job:{job_id}:status",
        json.dumps(
            {
                "job_id": job_id,
                "status": "queued",
                "result": None,
                "analysis_report_id": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ),
        ex=600,
    )
    return {"status": "queued", "job_id": job_id}


@router.get(
    "/analysis-reports/{company_id}",
    response_model=List[AnalysisReportResponse],
)
async def get_reports_for_company(company_id: UUID, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.company_id == company_id).order_by(AnalysisReport.created_at.asc())
    )
    reports = result.scalars().all()
    return reports


@router.get("/news/{company_id}", response_model=List[NewsResponse])
async def get_company_news(company_id: UUID, company_name: str, db: AsyncSession = Depends(get_async_db)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Check DB for today’s news
    db_result = await db.execute(
        select(CompanyNews).where(
            CompanyNews.company_id == company_id,
            CompanyNews.published_at >= today_start,
        )
    )
    existing_news = db_result.scalars().all()

    if existing_news:
        return existing_news

    # 2. Fetch fresh news
    fetched_news = await fetch_company_news(company_name, company_id)
    new_records = [
        CompanyNews(
            **{
                **news.dict(),
                "url": str(news.url),
                "image_url": str(news.image_url) if news.image_url else None,
            }
        )
        for news in fetched_news
    ]

    db.add_all(new_records)
    await db.commit()
    return new_records
