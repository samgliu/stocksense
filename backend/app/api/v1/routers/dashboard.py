from datetime import datetime, timedelta, timezone

from app.database import get_async_db
from app.dependencies.user_validation import get_current_user
from app.models.company import Company
from app.models.company_news import CompanyNews
from app.models.mock_account_snapshot import MockAccountSnapshot
from app.models.mock_transaction import MockTransaction
from app.models.stock_entry import StockEntry
from app.models.usage_log import UsageLog
from app.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/snapshots/daily")
async def get_snapshots_daily(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    user_id = str(current_user.id)
    stmt = select(
        MockAccountSnapshot.date,
        MockAccountSnapshot.total_value,
        MockAccountSnapshot.account_id,
        MockAccountSnapshot.user_id,
    ).where(MockAccountSnapshot.user_id == user_id)
    stmt = stmt.order_by(MockAccountSnapshot.date)
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "date": str(r.date),
            "total_value": r.total_value,
            "account_id": str(r.account_id),
            "user_id": r.user_id,
        }
        for r in rows
    ]


@router.get("/daily-analysis")
async def get_daily_analysis(db: AsyncSession = Depends(get_async_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = today - timedelta(days=30)

    stmt = (
        select(
            func.date(StockEntry.created_at).label("date"),
            func.count(StockEntry.id).label("count"),
        )
        .where(StockEntry.created_at >= start_date)
        .group_by(func.date(StockEntry.created_at))
        .order_by(func.date(StockEntry.created_at))
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [{"date": str(r.date), "count": r.count} for r in rows]


@router.get("/monthly-summary")
async def get_monthly_summary(db: AsyncSession = Depends(get_async_db)):
    today = datetime.now(timezone.utc)
    start_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)

    stmt = select(
        func.count().filter(StockEntry.created_at >= start_of_this_month),
        func.count().filter(
            StockEntry.created_at >= start_of_last_month,
            StockEntry.created_at < start_of_this_month,
        ),
    )
    current_month_count, last_month_count = (await db.execute(stmt)).one()

    return {
        "current_month_count": current_month_count,
        "last_month_count": last_month_count,
    }


@router.get("/history-summary")
async def get_history_summary(db: AsyncSession = Depends(get_async_db)):
    total_records_stmt = select(func.count(StockEntry.id))
    total_users_stmt = select(func.count(User.id))

    total_records = (await db.execute(total_records_stmt)).scalar()
    total_users = (await db.execute(total_users_stmt)).scalar()

    return {"total_records": total_records, "total_users": total_users}


@router.get("/usage-count")
async def get_usage_count(db: AsyncSession = Depends(get_async_db)):
    stmt = (
        select(User.role, func.count(func.distinct(UsageLog.id)).label("usage_count"))
        .join(UsageLog, UsageLog.user_id == User.id)
        .group_by(User.role)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return {role.value: count for role, count in rows}


@router.get("/top-companies")
async def get_top_companies(db: AsyncSession = Depends(get_async_db)):
    stmt = (
        select(StockEntry.text_input, func.count().label("count"))
        .group_by(StockEntry.text_input)
        .order_by(func.count().desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"ticker": r.text_input, "count": r.count} for r in rows]


@router.get("/news-summary")
async def get_news_summary(db: AsyncSession = Depends(get_async_db)):
    start = datetime.now(timezone.utc) - timedelta(days=7)
    stmt = (
        select(func.date(CompanyNews.published_at), func.count())
        .where(CompanyNews.published_at >= start)
        .group_by(func.date(CompanyNews.published_at))
        .order_by(func.date(CompanyNews.published_at))
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"date": str(r[0]), "count": r[1]} for r in rows]


@router.get("/top-industries")
async def get_top_sectors(db: AsyncSession = Depends(get_async_db)):
    stmt = (
        select(Company.sector, func.count(StockEntry.text_input))
        .join(Company, Company.ticker == StockEntry.text_input)
        .where(Company.sector.isnot(None))
        .group_by(Company.sector)
        .order_by(func.count(StockEntry.text_input).desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"sector": r[0], "count": r[1]} for r in rows]


@router.get("/buy-sell-daily")
async def get_buy_sell_daily(db: AsyncSession = Depends(get_async_db)):
    today = datetime.now(timezone.utc)
    start_date = today - timedelta(days=90)

    stmt = (
        select(
            func.date_trunc("day", MockTransaction.timestamp).label("date"),
            MockTransaction.action,
            func.sum(MockTransaction.amount * MockTransaction.price).label("total_spent"),
        )
        .where(MockTransaction.timestamp >= start_date)
        .group_by("date", MockTransaction.action)
        .order_by("date")
    )
    result = await db.execute(stmt)
    rows = result.all()

    daily_map = {}
    for date, action, total in rows:
        key = str(date.date())
        if key not in daily_map:
            daily_map[key] = {"date": key, "buy": 0, "sell": 0}
        daily_map[key][action] = round(total, 2)

    return list(daily_map.values())
