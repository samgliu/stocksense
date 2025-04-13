from app.kafka.producer import send_autotrade_job
from sqlalchemy.future import select
from app.models.auto_trade_subscription import AutoTradeSubscription
from app.database import get_async_db
import uuid


async def run_autotrade_cron():
    print("🚀 Running AutoTrader Cron", flush=True)

    db_gen = get_async_db()
    db = await anext(db_gen)

    try:
        result = await db.execute(
            select(AutoTradeSubscription).where(AutoTradeSubscription.active == True)
        )
        subs = result.scalars().all()

        for sub in subs:
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
            print(f"[AutoTrader Cron] Queued {sub.ticker} ({job_id})", flush=True)

    finally:
        await db_gen.aclose()  # close the generator
