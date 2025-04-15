from fastapi import Depends, HTTPException, Request, status
from app.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from sqlalchemy import select

async def get_current_user(request: Request, db: AsyncSession = Depends(get_async_db)):
    user_data = getattr(request.state, "user", None)
    if not user_data or "uid" not in user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    result = await db.execute(
        select(User).where(User.firebase_uid == user_data["uid"])
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

async def verify_user_ownership(
    user_id: int,  # or str, depending on your User model
    current_user: User = Depends(get_current_user)
):
    if str(current_user.id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Not your resource")
    return True
