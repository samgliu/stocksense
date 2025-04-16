from app.kafka.producer import send_autotrade_job
from sqlalchemy.future import select
from app.models.auto_trade_subscription import AutoTradeSubscription
from datetime import datetime, timezone, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mock_account import MockAccount
from app.models.mock_account_snapshot import MockAccountSnapshot
from app.models.mock_position import MockPosition
from sqlalchemy.future import select
from datetime import datetime
from app.services.yf_data import fetch_current_price

# Frequency mapping
FREQUENCY_INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


async def run_snapshot_cron(db):
    print("📸 Running Account Snapshot Cron", flush=True)
    try:
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
    except Exception as e:
        print(f"❌ Error in snapshot cron: {e}", flush=True)


async def run_autotrade_cron(db: AsyncSession, force: bool = False):
    print("🚀 Running AutoTrader Cron", flush=True)

    try:
        result = await db.execute(
            select(AutoTradeSubscription).where(AutoTradeSubscription.active == True)
        )
        subs = result.scalars().all()
        now = datetime.now(timezone.utc)

        for sub in subs:
            interval = FREQUENCY_INTERVALS.get(sub.frequency)
            if not interval and not force:
                print(
                    f"⚠️ Unknown frequency: {sub.frequency} — Skipping {sub.ticker}",
                    flush=True,
                )
                continue

            last_run = sub.last_run_at or datetime.min.replace(tzinfo=timezone.utc)
            if not force and (now - last_run < interval):
                print(
                    f"⏳ Skipping {sub.ticker} — Not enough time since last run ({sub.frequency})",
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

    except Exception as e:
        print(f"❌ Error in AutoTrader Cron: {e}", flush=True)
