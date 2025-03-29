from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta, timezone

from app.database import get_async_db
from app.models.stock_entry import StockEntry
from app.models.user import User
from app.models.usage_log import UsageLog

router = APIRouter()


@router.get("/daily-analysis")
async def get_daily_analysis(db: AsyncSession = Depends(get_async_db)):
    today = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_date = today - timedelta(days=30)

    stmt = (
        select(
            func.date(StockEntry.created_at).label("date"),
            func.count(StockEntry.id).label("count"),
        )
        .where(StockEntry.created_at >= start_date)
        .group_by(func.date(StockEntry.created_at))
        .order_by("date")
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [{"date": str(r.date), "count": r.count} for r in rows]


@router.get("/monthly-summary")
async def get_monthly_summary(db: AsyncSession = Depends(get_async_db)):
    today = datetime.now(timezone.utc)
    start_of_this_month = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)

    current_month_stmt = select(func.count()).where(
        StockEntry.created_at >= start_of_this_month
    )
    last_month_stmt = select(func.count()).where(
        StockEntry.created_at >= start_of_last_month,
        StockEntry.created_at < start_of_this_month,
    )

    current_month_count = (await db.execute(current_month_stmt)).scalar()
    last_month_count = (await db.execute(last_month_stmt)).scalar()

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
        select(User.role, func.count(UsageLog.id).label("usage_count"))
        .join(UsageLog, UsageLog.user_id == User.id)
        .group_by(User.role)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return {role.value: count for role, count in rows}
