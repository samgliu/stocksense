import asyncio
import logging
import os
import threading

import sentry_sdk
from prometheus_client import Counter

from app.consumers.analysis_consumer import run_analysis_consumer
from app.consumers.analysis_consumer_stream import run_analysis_consumer_stream
from app.consumers.autotrade_consumer import run_autotrade_consumer
from app.utils.metrics_server import start_metrics_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

logger = logging.getLogger("stocksense")

# Prometheus metrics
WORKER_TASKS_TOTAL = Counter("worker_tasks_total", "Total tasks processed by the worker")
WORKER_ERRORS_TOTAL = Counter("worker_errors_total", "Total errors in worker tasks")


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0,
    sample_rate=0.1,
    environment=os.getenv("ENV", "production"),
    send_default_pii=True,
)


def log_task_exception(task):
    try:
        exc = task.exception()
        if exc:
            WORKER_ERRORS_TOTAL.inc()
            logger.error(f"⚠️ Unhandled exception in consumer task: {exc}")
    except asyncio.CancelledError:
        pass


async def main():
    logger.info("🚀 Worker starting up")

    threading.Thread(target=start_metrics_server, daemon=True).start()

    tasks = [
        asyncio.create_task(run_analysis_consumer()),
        asyncio.create_task(run_autotrade_consumer()),
        asyncio.create_task(run_analysis_consumer_stream()),
    ]
    for t in tasks:
        t.add_done_callback(log_task_exception)

    # Keep main alive forever
    await asyncio.Event().wait()


def handle_uncaught(loop, context):
    msg = context.get("exception", context["message"])
    logger.error(f"Caught global exception: {msg}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_uncaught)
    loop.run_until_complete(main())
