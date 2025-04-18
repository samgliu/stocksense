from app.models.mock_account import MockAccount
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.database import get_async_db
from app.models.user import User, UserRole
from app.models.usage_log import UsageLog

from app.schemas.user import UserOut


router = APIRouter()


@router.get("/auth", response_model=UserOut)
async def auth_verify(request: Request, db: AsyncSession = Depends(get_async_db)):
    user_data = request.state.user

    email = user_data.get("email")
    name = user_data.get("name")
    firebase_uid = user_data.get("uid")

    # Fetch user
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if not user:
        if email == "samgliu19@gmail.com":
            role = UserRole.ADMIN
        elif email == "guest@stocksense.dev":
            role = UserRole.ANONYMOUS
        else:
            role = UserRole.USER

        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name or "Anonymous",
            role=role,
            verified=True,
            last_login=now,
        )
        db.add(user)
        await db.flush()  # ensure user.id is generated before next step
    else:
        user.last_login = now

    # Ensure mock account exists
    existing_account = await db.execute(
        select(MockAccount).where(MockAccount.user_id == str(user.id))
    )
    if not existing_account.scalar_one_or_none():
        db.add(MockAccount(user_id=str(user.id), balance=1_000_000.0))

    await db.commit()
    await db.refresh(user)

    # Get today's usage count
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    usage_count_result = await db.execute(
        select(func.count(UsageLog.id)).filter(
            UsageLog.user_id == user.id,
            UsageLog.created_at >= start_of_day,
            UsageLog.created_at < end_of_day,
        )
    )
    usage_count_today = usage_count_result.scalar_one()

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "verified": user.verified,
        "usage_count_today": usage_count_today,
    }
