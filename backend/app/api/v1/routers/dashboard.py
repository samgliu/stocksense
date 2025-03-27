from app.models.usage_log import UsageLog
from app.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.stock_entry import StockEntry

router = APIRouter()


@router.get("/daily-analysis")
def get_daily_analysis(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_date = today - timedelta(days=30)  # last 30 days including today

    results = (
        db.query(
            func.date(StockEntry.created_at).label("date"),
            func.count(StockEntry.id).label("count"),
        )
        .filter(StockEntry.created_at >= start_date)
        .group_by(func.date(StockEntry.created_at))
        .order_by("date")
        .all()
    )

    return [{"date": str(r.date), "count": r.count} for r in results]


@router.get("/monthly-summary")
def get_monthly_summary(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc)
    start_of_this_month = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)

    current_month_count = (
        db.query(func.count(StockEntry.id))
        .filter(StockEntry.created_at >= start_of_this_month)
        .scalar()
    )

    last_month_count = (
        db.query(func.count(StockEntry.id))
        .filter(
            StockEntry.created_at >= start_of_last_month,
            StockEntry.created_at < start_of_this_month,
        )
        .scalar()
    )

    return {
        "current_month_count": current_month_count,
        "last_month_count": last_month_count,
    }


@router.get("/history-summary")
def get_history_summary(db: Session = Depends(get_db)):
    total_records = db.query(StockEntry).count()
    total_users = db.query(User).count()

    return {"total_records": total_records, "total_users": total_users}


@router.get("/usage-count")
def get_usage_count(db: Session = Depends(get_db)):
    usage_by_role = (
        db.query(User.role, func.count(UsageLog.id).label("usage_count"))
        .join(UsageLog, UsageLog.user_id == User.id)
        .group_by(User.role)
        .all()
    )
    return {role: count for role, count in usage_by_role}
