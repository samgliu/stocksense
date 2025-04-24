import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import UUID

import httpx
import numpy as np
import pandas as pd
import yfinance as yf
from app.database import AsyncSessionLocal
from app.models.auto_trade_subscription import AutoTradeSubscription
from app.models.company import Company
from app.models.mock_account import MockAccount
from app.models.mock_position import MockPosition
from app.models.mock_transaction import MockTransaction
from app.models.trade_report import TradeDecision, TradeReport
from sqlalchemy.future import select

logger = logging.getLogger("stocksense")


async def get_company_from_db(company_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.id == UUID(company_id)))
        company = result.scalar_one_or_none()

        if not company:
            raise ValueError(f"❌ Company with ID {company_id} not found.")

        return {
            "id": str(company.id),
            "name": company.name,
            "ticker": company.ticker,
            "shortname": company.shortname,
            "exchange": company.exchange,
            "sector": company.sector,
            "industry": company.industry,
            "country": company.country,
            "summary": company.summary,
            "insights": company.insights,
            "website": company.website,
            "current_price": (float(company.current_price) if company.current_price else None),
            "market_cap": float(company.market_cap) if company.market_cap else None,
            "ebitda": float(company.ebitda) if company.ebitda else None,
            "revenue_growth": company.revenue_growth,
            "fulltime_employees": (int(company.fulltime_employees) if company.fulltime_employees else None),
        }


async def fetch_user_holdings_from_db(user_id: str, ticker: str) -> Optional[dict]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MockPosition).where(MockPosition.account_id == user_id, MockPosition.ticker == ticker)
        )
        position = result.scalar_one_or_none()

        if not position:
            # Still return balance if account exists
            account_result = await db.execute(select(MockAccount).where(MockAccount.user_id == user_id))
            account = account_result.scalar_one_or_none()
            return {"balance": float(account.balance) if account else 0}

        # Fetch associated account balance
        account_result = await db.execute(select(MockAccount).where(MockAccount.id == position.account_id))
        account = account_result.scalar_one_or_none()

        return {
            "ticker": position.ticker,
            "shares": position.shares,
            "average_cost": position.average_cost,
            "last_updated": (position.updated_at.isoformat() if position.updated_at else None),
            "balance": float(account.balance) if account else 0,
        }


async def fetch_historical_prices(ticker: str, days: int = 90) -> List[Dict]:
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    logger.info(f"Fetching historical prices for {ticker} from {start_date} to {end_date}")

    data = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        return []

    if isinstance(data["Close"], pd.DataFrame):
        close_series = data["Close"][ticker]
    else:
        close_series = data["Close"]

    result = [{"date": date.strftime("%Y-%m-%d"), "close": round(close, 2)} for date, close in close_series.items()]

    return result


async def fetch_current_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice")
    if not price:
        raise ValueError(f"⚠️ No real-time price available for {ticker}")
    return round(price, 2)


FMP_API_KEY = os.getenv("FMP_API_KEY")
FMP_RATIOS_URL = "https://financialmodelingprep.com/stable/ratios-ttm"


async def fetch_fundamentals_fmp(ticker: str) -> Optional[dict]:
    url = f"{FMP_RATIOS_URL}?symbol={ticker}&apikey={FMP_API_KEY}"

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"❌ Error fetching FMP fundamentals for {ticker}: {e}")
            return None

    if not data or not isinstance(data, list) or len(data) == 0:
        logger.warning(f"⚠️ No TTM ratios found for {ticker}")
        return None

    return data[0]


async def persist_result_to_db(payload: dict, result: dict, current_price: float):
    user_id = payload.get("user_id")
    company_id = payload.get("company_id")
    subscription_id = payload.get("subscription_id")
    ticker = payload.get("ticker")
    decision_raw = result.get("decision")
    decision = decision_raw.lower() if isinstance(decision_raw, str) else None
    try:
        price = current_price or result.get("price")
    except Exception:
        price = result.get("price")

    shares_to_trade = result.get("amount")

    if not all([user_id, ticker, decision, price]):
        logger.error("❌ Missing required fields; skipping persistence.")
        return

    async with AsyncSessionLocal() as db:
        # Fetch account
        account_result = await db.execute(select(MockAccount).where(MockAccount.user_id == user_id))
        account = account_result.scalar_one_or_none()
        if not account:
            logger.error(f"❌ No mock account found for user {user_id}")
            return

        account_id = account.id

        # Fetch existing position
        position_result = await db.execute(
            select(MockPosition).where(
                MockPosition.account_id == account_id,
                MockPosition.ticker == ticker,
            )
        )
        position = position_result.scalar_one_or_none()

        if decision in ("buy", "sell") and shares_to_trade and shares_to_trade > 0:
            realized_gain = None
            if decision == "sell" and position and position.shares >= shares_to_trade:
                gain_per_share = price - position.average_cost
                realized_gain = gain_per_share * shares_to_trade

            tx = MockTransaction(
                id=uuid.uuid4(),
                account_id=account_id,
                ticker=ticker,
                action=TradeDecision(decision),
                amount=shares_to_trade,
                price=price,
                realized_gain=realized_gain,
            )
            db.add(tx)

            if decision == "buy":
                cost = shares_to_trade * price
                if account.balance < cost:
                    logger.warning(f"⚠️ Insufficient balance: ${account.balance} < ${cost}")
                    return

                if position:
                    total_shares = position.shares + shares_to_trade
                    new_avg_cost = (position.shares * position.average_cost + cost) / total_shares
                    position.shares = total_shares
                    position.average_cost = new_avg_cost
                else:
                    position = MockPosition(
                        id=uuid.uuid4(),
                        account_id=account_id,
                        ticker=ticker,
                        shares=shares_to_trade,
                        average_cost=price,
                    )
                    db.add(position)

                account.balance -= cost

            elif decision == "sell":
                if not position or position.shares < shares_to_trade:
                    logger.warning(f"⚠️ Not enough shares to sell: {position.shares if position else 0}")
                    return

                position.shares -= shares_to_trade
                account.balance += shares_to_trade * price
                sell_amount = shares_to_trade
                gain_per_share = price - position.average_cost
                realized_gain = gain_per_share * sell_amount
                if position.shares == 0:
                    position.average_cost = 0

            logger.info(f"✅ Trade persisted: {decision.upper()} {shares_to_trade} {ticker} @ ${price:.2f}")
        else:
            logger.info(f"ℹ️ Decision is '{decision_raw}', skipping transaction.")

        # Always record a TradeReport, regardless of action
        trade_report = TradeReport(
            id=uuid.uuid4(),
            subscription_id=subscription_id,
            user_id=user_id,
            company_id=company_id,
            ticker=ticker,
            decision=TradeDecision(decision) if decision else None,
            reason=result.get("reason", "No reason provided."),
            payload=payload,
        )
        db.add(trade_report)

        sub_result = await db.execute(select(AutoTradeSubscription).where(AutoTradeSubscription.id == subscription_id))
        sub = sub_result.scalar_one_or_none()
        if sub:
            sub.last_run_at = datetime.now(timezone.utc)
        await db.commit()
