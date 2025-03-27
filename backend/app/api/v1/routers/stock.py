from datetime import datetime, timezone
from app.core.config import USER_DAILY_LIMIT
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.usage_log import UsageLog
from app.models.stock_entry import StockEntry
from app.schemas.stock import StockRequest, StockResponse
from app.services.stock_analysis import analyze_stock
from app.core.decorators import verify_token

router = APIRouter()


@router.post("/analyze", response_model=StockResponse)
@verify_token
async def analyze_stock_endpoint(
    request: Request,
    body: StockRequest,
    db: Session = Depends(get_db),
):
    user_data = request.state.user
    user = db.query(User).filter(User.email == user_data["email"]).first()

    if user.role == UserRole.USER:
        start_of_day = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        usage_count_today = (
            db.query(UsageLog)
            .filter(UsageLog.user_id == user.id, UsageLog.created_at >= start_of_day)
            .count()
        )
        if usage_count_today >= USER_DAILY_LIMIT:
            raise HTTPException(status_code=429, detail="Daily usage limit reached")

    result = analyze_stock(body.text)

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

    db.commit()

    return {"summary": result}


@router.get("/history")
@verify_token
async def get_history(request: Request, db: Session = Depends(get_db)):
    user_data = request.state.user
    user = db.query(User).filter_by(email=user_data["email"]).first()

    entries = (
        db.query(StockEntry)
        .filter_by(user_id=user.id)
        .order_by(StockEntry.created_at.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "id": str(entry.id),
            "summary": entry.summary,
            "created_at": entry.created_at.isoformat(),
            "source_type": entry.source_type,
            "model_used": entry.model_used,
            "text_input": entry.text_input[:100] + "..." if entry.text_input else None,
        }
        for entry in entries
    ]
