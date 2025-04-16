from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from app.cron.runner import run_autotrade_cron, run_snapshot_cron
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


async def run_snapshot_cron_with_db():
    db_gen = get_async_db()
    db = await anext(db_gen)
    try:
        await run_snapshot_cron(db)
    finally:
        await db_gen.aclose()

def start_autotrade_scheduler():
    # Run the job at 9:30, 10:30, ..., 15:30 ET (Mon-Fri)
    scheduler.add_job(
        run_cron_job_with_db,
        "cron",
        day_of_week="mon-fri",
        hour="9-15",
        minute=30,
    )
    # Run the snapshot job at 16:05 ET (Mon-Fri)
    scheduler.add_job(
        run_snapshot_cron_with_db,
        "cron",
        day_of_week="mon-fri",
        hour=16,
        minute=5,
    )
    scheduler.start()
