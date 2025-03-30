from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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

    # Fetch user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if not user:
        user = User(
            email=email,
            name=name,
            role=UserRole.ADMIN if email == "samgliu19@gmail.com" else UserRole.USER,
            verified=True,
            last_login=now,
        )
        db.add(user)
    else:
        user.last_login = now

    await db.commit()
    await db.refresh(user)

    # Get today's usage count
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    usage_result = await db.execute(
        select(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.created_at >= start_of_day,
            UsageLog.created_at < end_of_day,
        )
    )
    usage_count_today = len(usage_result.scalars().all())

    return {
        "id": str(user.id),
        "email": user.email,
        "fullname": user.name,
        "role": user.role.value,
        "verified": user.verified,
        "usage_count_today": usage_count_today,
    }
