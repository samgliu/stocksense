from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from app.cron.runner import run_autotrade_cron
from app.database import get_async_db

eastern = timezone("US/Eastern")
scheduler = AsyncIOScheduler(timezone=eastern)


async def run_cron_job_with_db():
    db_gen = get_async_db()
    db = await anext(db_gen)
    try:
        await run_autotrade_cron(db)
    finally:
        await db_gen.aclose()


def start_autotrade_scheduler():
    scheduler.add_job(run_cron_job_with_db, "cron", hour=9, minute=30)
    scheduler.start()
