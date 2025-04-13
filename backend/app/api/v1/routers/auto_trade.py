from uuid import UUID
from app.models.company import Company
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.schemas.auto_trade import AutoTradeSubscriptionCreate, AutoTradeSubscriptionOut
from app.models.auto_trade_subscription import AutoTradeSubscription
from sqlalchemy.future import select
from typing import List

router = APIRouter()


@router.post("/subscribe", response_model=AutoTradeSubscriptionOut)
async def subscribe_to_auto_trade(
    subscription: AutoTradeSubscriptionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    # Check for existing subscription
    result = await db.execute(
        select(AutoTradeSubscription).where(
            AutoTradeSubscription.user_id == subscription.user_id,
            AutoTradeSubscription.company_id == subscription.company_id,
            AutoTradeSubscription.ticker == subscription.ticker,
        )
    )
    existing = result.scalars().first()

    # Fetch company name now (used for response either way)
    company_result = await db.execute(
        select(Company.name).where(Company.id == subscription.company_id)
    )
    company_name = company_result.scalar()

    if existing:
        if existing.active:
            raise HTTPException(
                status_code=400,
                detail="Active subscription already exists for this ticker.",
            )
        for field, value in subscription.dict().items():
            setattr(existing, field, value)
        existing.active = True
        await db.commit()
        await db.refresh(existing)
        return {**existing.__dict__, "company_name": company_name}

    # No existing → create new
    new_sub = AutoTradeSubscription(**subscription.dict())
    db.add(new_sub)
    await db.commit()
    await db.refresh(new_sub)
    return {**new_sub.__dict__, "company_name": company_name}


@router.put("/subscribe/{subscription_id}", response_model=AutoTradeSubscriptionOut)
async def update_subscription(
    subscription_id: UUID,
    update_data: AutoTradeSubscriptionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    sub = await db.get(AutoTradeSubscription, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    for field, value in update_data.dict().items():
        setattr(sub, field, value)

    await db.commit()
    await db.refresh(sub)

    # Return with company name
    result = await db.execute(select(Company.name).where(Company.id == sub.company_id))
    company_name = result.scalar()

    return {**sub.__dict__, "company_name": company_name}


@router.delete("/subscribe/{subscription_id}")
async def deactivate_subscription(
    subscription_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    sub = await db.get(AutoTradeSubscription, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub.active = False
    await db.commit()
    return {"detail": "Subscription deactivated"}


@router.get("/subscribe", response_model=List[AutoTradeSubscriptionOut])
async def get_user_subscriptions(
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(AutoTradeSubscription, Company.name)
        .join(Company, AutoTradeSubscription.company_id == Company.id)
        .where(
            AutoTradeSubscription.user_id == user_id,
            AutoTradeSubscription.active == True,
        )
        .order_by(AutoTradeSubscription.created_at.desc())
    )

    rows = result.all()
    return [
        {**sub.__dict__, "company_name": company_name} for sub, company_name in rows
    ]
