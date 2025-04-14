from app.kafka.producer import send_autotrade_job
from sqlalchemy.future import select
from app.models.auto_trade_subscription import AutoTradeSubscription
from datetime import datetime, timezone, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

# Frequency mapping
FREQUENCY_INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


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
