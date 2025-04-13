from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .runner import run_autotrade_cron

scheduler = AsyncIOScheduler()


def start_autotrade_scheduler():
    scheduler.add_job(run_autotrade_cron, "cron", minute=0)
    scheduler.start()
