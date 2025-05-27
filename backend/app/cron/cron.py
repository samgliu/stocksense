from app.cron.runner import run_autotrade_cron, run_snapshot_cron, run_trigger_qdrant_job
from app.database import get_async_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

eastern = timezone("US/Eastern")
scheduler = AsyncIOScheduler(timezone=eastern)


async def run_cron_job_with_db():
    gen = get_async_db()
    db = await gen.__anext__()
    try:
        await run_autotrade_cron(db)
    finally:
        await gen.aclose()


async def run_snapshot_cron_with_db():
    gen = get_async_db()
    db = await gen.__anext__()
    try:
        await run_snapshot_cron(db)
    finally:
        await gen.aclose()


async def run_weekly_search():
    """keep db active"""
    await run_trigger_qdrant_job()


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
    # Run the qdrant warmup job
    scheduler.add_job(
        run_trigger_qdrant_job,
        "cron",
        day_of_week="mon,thu",
        hour=9,
        minute=0,
    )
    scheduler.start()
