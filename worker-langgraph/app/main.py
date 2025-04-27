import asyncio
import logging
import os
import signal
import threading

import sentry_sdk
from aiokafka.errors import KafkaConnectionError, NodeNotReadyError
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


def before_send(event, hint):
    if "exc_info" in hint:
        exc_type, exc_value, _ = hint["exc_info"]
        if isinstance(exc_value, (KafkaConnectionError, NodeNotReadyError)):
            return None
    return event


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0,
    sample_rate=0.1,
    environment=os.getenv("ENV", "production"),
    send_default_pii=True,
    before_send=before_send,
)


def log_task_exception(task):
    try:
        exc = task.exception()
        if exc:
            WORKER_ERRORS_TOTAL.inc()
            logger.error(f"⚠️ Unhandled exception in consumer task: {exc}")
    except asyncio.CancelledError:
        pass


def handle_uncaught(loop, context):
    msg = context.get("exception", context["message"])
    logger.error(f"Caught global exception: {msg}")


async def main():
    logger.info("🚀 Worker starting up")
    shutdown_event = asyncio.Event()

    threading.Thread(target=start_metrics_server, daemon=True).start()

    loop = asyncio.get_running_loop()
    loop.set_exception_handler(handle_uncaught)
    loop.add_signal_handler(signal.SIGINT, shutdown_event.set)
    loop.add_signal_handler(signal.SIGTERM, shutdown_event.set)

    tasks = [
        asyncio.create_task(run_analysis_consumer(shutdown_event)),
        asyncio.create_task(run_autotrade_consumer(shutdown_event)),
        asyncio.create_task(run_analysis_consumer_stream(shutdown_event)),
    ]
    for t in tasks:
        t.add_done_callback(log_task_exception)

    await shutdown_event.wait()
    logger.info("📦 Shutting down consumers...")

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.info("👋 Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
