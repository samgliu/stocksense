from uuid import UUID
from app.models.company import Company
from app.cron.runner import run_autotrade_cron
from app.models.user import User, UserRole
from app.models.mock_account import MockAccount
from app.models.mock_transaction import MockTransaction
from app.models.mock_position import MockPosition
from app.services.yf_data import fetch_current_price
from fastapi import APIRouter, Depends, Query, HTTPException, Request, status
from app.dependencies.user_validation import get_current_user, verify_user_ownership
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
    current_user: User = Depends(get_current_user),
):
    # Enforce user ownership
    if str(subscription.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden: Not your resource")
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

    # Count active subscriptions for the user
    active_result = await db.execute(
        select(AutoTradeSubscription)
        .where(AutoTradeSubscription.user_id == subscription.user_id)
        .where(AutoTradeSubscription.active == True)
    )
    active_subs = active_result.scalars().all()

    if len(active_subs) >= 3:
        raise HTTPException(
            status_code=400,
            detail="You can only have up to 3 active auto-trade subscriptions.",
        )

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
    current_user: User = Depends(get_current_user),
):
    sub = await db.get(AutoTradeSubscription, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if str(sub.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden: Not your resource")

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
    current_user: User = Depends(get_current_user),
):
    sub = await db.get(AutoTradeSubscription, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if str(sub.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden: Not your resource")

    sub.active = False
    await db.commit()
    return {"detail": "Subscription deactivated"}


@router.get("/subscribe")
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    user_id = str(current_user.id)
    result = await db.execute(
        select(AutoTradeSubscription, Company.name, Company.ticker)
        .join(Company, AutoTradeSubscription.company_id == Company.id)
        .where(AutoTradeSubscription.user_id == user_id)
        .order_by(AutoTradeSubscription.created_at.desc())
    )
    rows = result.all()

    account_result = await db.execute(
        select(MockAccount).where(MockAccount.user_id == user_id)
    )
    account = account_result.scalar_one_or_none()
    balance = float(account.balance) if account else 0

    subscriptions = []
    total_invested = 0
    total_unrealized_gain = 0

    for sub, company_name, ticker in rows:
        try:
            current_price_float = await fetch_current_price(ticker)
        except Exception as e:
            print(f"⚠️ Failed to fetch price for {ticker}: {e}")
            current_price_float = 0

        tx_result = await db.execute(
            select(MockTransaction)
            .where(
                MockTransaction.account_id == account.id,
                MockTransaction.ticker == ticker,
            )
            .order_by(MockTransaction.timestamp.desc())
        )
        transactions = [tx.__dict__ for tx in tx_result.scalars().all()]

        position_result = await db.execute(
            select(MockPosition).where(
                MockPosition.account_id == account.id,
                MockPosition.ticker == ticker,
            )
        )
        position = position_result.scalar_one_or_none()

        if position:
            shares = position.shares
            avg_cost = float(position.average_cost)
            market_value = shares * current_price_float
            unrealized_gain = (current_price_float - avg_cost) * shares
            gain_pct = (
                (unrealized_gain / (avg_cost * shares)) * 100 if avg_cost > 0 else 0
            )

            total_invested += market_value
            total_unrealized_gain += unrealized_gain
        else:
            shares = 0
            avg_cost = 0
            market_value = 0
            unrealized_gain = 0
            gain_pct = 0

        subscriptions.append(
            {
                **sub.__dict__,
                "company_name": company_name,
                "transactions": transactions,
                "holding_summary": {
                    "shares": shares,
                    "average_cost": round(avg_cost, 2),
                    "current_price": round(current_price_float, 2),
                    "market_value": round(market_value, 2),
                    "unrealized_gain": round(unrealized_gain, 2),
                    "gain_pct": round(gain_pct, 2),
                },
            }
        )

    return {
        "balance": round(balance, 2),
        "portfolio_value": round(total_invested, 2),
        "total_value": round(balance + total_invested, 2),
        "total_return": round(total_unrealized_gain, 2),
        "subscriptions": subscriptions,
    }


@router.post("/reset")
async def reset_balance(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    account_result = await db.execute(
        select(MockAccount).where(MockAccount.user_id == str(current_user.id))
    )
    account = account_result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Mock account not found")

    account.balance = 1_000_000.0
    await db.commit()
    await db.refresh(account)

    return {"detail": "Balance reset to $1,000,000", "balance": account.balance}


@router.post("/force-run")
async def force_run_autotrade_cron(
    request: Request, db: AsyncSession = Depends(get_async_db)
):
    user_data = request.state.user
    user_result = await db.execute(
        select(User).where(User.firebase_uid == user_data["uid"])
    )
    user = user_result.scalar_one_or_none()

    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can force run the AutoTrader job.",
        )

    await run_autotrade_cron(db=db, force=True)
    return {"detail": "AutoTrader cron job executed manually"}
