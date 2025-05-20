import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from app.kafka.producer import send_autotrade_job
from app.models.auto_trade_subscription import AutoTradeSubscription
from app.models.mock_account import MockAccount
from app.models.mock_account_snapshot import MockAccountSnapshot
from app.models.mock_position import MockPosition
from app.services.yf_data import fetch_current_price
from pytz import timezone as pytz_timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Frequency mapping
FREQUENCY_INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}
QDRANT_URL = os.environ["QDRANT_CLOUD_URL"]
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]


logger = logging.getLogger("stocksense")


async def run_snapshot_cron(db):
    logger.info("📸 Running Account Snapshot Cron")
    accounts_result = await db.execute(select(MockAccount))
    accounts = accounts_result.scalars().all()

    skipped_accounts = 0
    saved_snapshots = 0

    for account in accounts:
        logger.info(f"📊 Processing snapshot for account {account.id}")
        positions_result = await db.execute(select(MockPosition).where(MockPosition.account_id == account.id))
        positions = positions_result.scalars().all()

        portfolio_value = 0.0
        snapshot_failed = False

        for pos in positions:
            try:
                price = await fetch_current_price(pos.ticker)
                portfolio_value += price * (pos.shares or 0)
            except Exception as e:
                logger.error(f"⚠️ Skipping account {account.id} due to price fetch failure for {pos.ticker}: {e}")
                snapshot_failed = True
                break

        if snapshot_failed:
            skipped_accounts += 1
            continue

        balance = account.balance or 0.0
        total_value = portfolio_value + balance
        initial_balance = 1_000_000.0
        return_pct = (total_value / initial_balance) - 1

        snapshot = MockAccountSnapshot(
            account_id=account.id,
            user_id=account.user_id,
            date=datetime.now().date(),
            balance=balance,
            portfolio_value=portfolio_value,
            total_value=total_value,
            return_pct=return_pct,
        )

        db.add(snapshot)
        saved_snapshots += 1

    await db.commit()
    logger.info(
        f"✅ Snapshots completed: {saved_snapshots} accounts saved, "
        f"{skipped_accounts} accounts skipped due to price fetch errors."
    )


def is_market_open(now_eastern):
    # Market open: 9:30 to 16:00 ET, Mon-Fri
    if now_eastern.weekday() >= 5:
        return False
    open_time = now_eastern.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = now_eastern.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_time <= now_eastern < close_time


async def run_autotrade_cron(db: AsyncSession, force: bool = False):
    logger.info("🚀 Running AutoTrader Cron")
    eastern = pytz_timezone("US/Eastern")
    now_utc = datetime.now(timezone.utc)
    now_eastern = now_utc.astimezone(eastern)
    if not force and not is_market_open(now_eastern):
        logger.info(f"⏰ Market is closed at {now_eastern.strftime('%Y-%m-%d %H:%M:%S %Z')} — Skipping all jobs")
        return

    result = await db.execute(select(AutoTradeSubscription).where(AutoTradeSubscription.active))
    subs = result.scalars().all()
    SAFE_MIN = datetime(2000, 1, 1, tzinfo=timezone.utc)

    for sub in subs:
        last_run = sub.last_run_at or SAFE_MIN
        last_run_eastern = last_run.astimezone(eastern)

        should_run = False
        if sub.frequency == "hourly":
            should_run = (now_utc - last_run) >= timedelta(hours=1)
        elif sub.frequency == "daily":
            # Only run if last_run is not today (Eastern)
            should_run = last_run_eastern.date() != now_eastern.date()
        elif sub.frequency == "weekly":
            # Only run if last_run is not this week (Eastern)
            should_run = not (
                last_run_eastern.isocalendar()[1] == now_eastern.isocalendar()[1]
                and last_run_eastern.year == now_eastern.year
            )
        else:
            logger.info(f"⚠️ Unknown frequency: {sub.frequency} — Skipping {sub.ticker}")
            continue

        if not force and not should_run:
            logger.info(f"⏳ Skipping {sub.ticker} — Not time to run yet (frequency: {sub.frequency})")
            continue

        job_id = str(uuid.uuid4())
        payload = {
            "job_id": job_id,
            "subscription_id": str(sub.id),
            "user_id": sub.user_id,
            "company_id": str(sub.company_id),
            "ticker": sub.ticker,
            "frequency": sub.frequency,
            "risk_tolerance": sub.risk_tolerance,
            "wash_sale": sub.wash_sale,
        }

        await send_autotrade_job(payload)
        logger.info(f"✅ Queued {sub.ticker} ({job_id})")

    await db.commit()
    logger.info("✅ AutoTrader cron completed")


async def run_trigger_qdrant_job():
    vector = [0.0] * 384
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{QDRANT_URL}/collections/sp500/points/search",
                headers={"api-key": QDRANT_API_KEY, "Content-Type": "application/json"},
                json={"vector": vector, "top": 1, "with_payload": False},
            )
            response.raise_for_status()
            logger.info("✅ Qdrant warmup ping succeeded")
    except Exception as e:
        logger.warning(f"⚠️ Qdrant warmup ping failed: {e}")
