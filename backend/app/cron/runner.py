from app.kafka.producer import send_autotrade_job
from sqlalchemy.future import select
from app.models.auto_trade_subscription import AutoTradeSubscription
from datetime import datetime, timezone, timedelta
from pytz import timezone as pytz_timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mock_account import MockAccount
from app.models.mock_account_snapshot import MockAccountSnapshot
from app.models.mock_position import MockPosition
from app.services.yf_data import fetch_current_price

# Frequency mapping
FREQUENCY_INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


async def run_snapshot_cron(db):
    print("📸 Running Account Snapshot Cron", flush=True)
    accounts = await db.execute(select(MockAccount))
    accounts = accounts.scalars().all()
    for account in accounts:
        positions = await db.execute(
            select(MockPosition).where(MockPosition.account_id == account.id)
        )
        positions = positions.scalars().all()
        portfolio_value = 0.0
        for pos in positions:
            try:
                price = await fetch_current_price(pos.ticker)
            except Exception as e:
                print(f"⚠️ Could not fetch price for {pos.ticker}: {e}", flush=True)
                price = 0.0
            portfolio_value += price * (pos.shares or 0)
        balance = account.balance or 0.0
        total_value = portfolio_value + balance
        initial_balance = 1000000.0
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
    await db.commit()
    print("✅ Snapshots taken for all accounts.", flush=True)


def is_market_open(now_eastern):
    # Market open: 9:30 to 16:00 ET, Mon-Fri
    if now_eastern.weekday() >= 5:
        return False
    open_time = now_eastern.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = now_eastern.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_time <= now_eastern < close_time


async def run_autotrade_cron(db: AsyncSession, force: bool = False):
    print("🚀 Running AutoTrader Cron", flush=True)
    eastern = pytz_timezone("US/Eastern")
    now_utc = datetime.now(timezone.utc)
    now_eastern = now_utc.astimezone(eastern)
    if not force and not is_market_open(now_eastern):
        print(
            f"⏰ Market is closed at {now_eastern.strftime('%Y-%m-%d %H:%M:%S %Z')} — Skipping all jobs",
            flush=True,
        )
        return

    result = await db.execute(
        select(AutoTradeSubscription).where(AutoTradeSubscription.active)
    )
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
            print(
                f"⚠️ Unknown frequency: {sub.frequency} — Skipping {sub.ticker}",
                flush=True,
            )
            continue

        if not force and not should_run:
            print(
                f"⏳ Skipping {sub.ticker} — Not time to run yet (frequency: {sub.frequency})",
                flush=True,
            )
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
        print(f"✅ Queued {sub.ticker} ({job_id})", flush=True)

    await db.commit()
    print("✅ AutoTrader cron completed", flush=True)
