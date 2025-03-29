from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.config import USER_DAILY_LIMIT
from app.core.decorators import verify_token
from app.database import get_async_db
from app.models.user import User, UserRole
from app.models.usage_log import UsageLog
from app.models.stock_entry import StockEntry
from app.schemas.stock_entry import StockRequest, StockResponse, StockHistoryItem
from app.services.stock_analysis import analyze_stock

router = APIRouter()


@router.post("/analyze", response_model=StockResponse)
@verify_token
async def analyze_stock_endpoint(
    request: Request,
    body: StockRequest,
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

    result = await analyze_stock(body.text)

    entry = StockEntry(
        user_id=user.id,
        text_input=body.text,
        summary=result,
        source_type="text",
        model_used="gemini",
    )
    db.add(entry)

    usage_log = UsageLog(user_id=user.id, action="analyze")
    db.add(usage_log)

    await db.commit()

    return StockResponse(summary=result)


@router.get("/history", response_model=list[StockHistoryItem])
@verify_token
async def get_history(request: Request, db: AsyncSession = Depends(get_async_db)):
    user_data = request.state.user
    user_result = await db.execute(select(User).where(User.email == user_data["email"]))
    user = user_result.scalar_one()

    entries_result = await db.execute(
        select(StockEntry)
        .where(StockEntry.user_id == user.id)
        .order_by(StockEntry.created_at.desc())
        .limit(20)
    )
    entries = entries_result.scalars().all()

    return entries
