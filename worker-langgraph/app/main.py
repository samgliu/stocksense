import asyncio
import os
import threading

import sentry_sdk
from prometheus_client import Counter
from app.utils.metrics_server import start_metrics_server

from app.consumers.analysis_consumer import run_analysis_consumer
from app.consumers.autotrade_consumer import run_autotrade_consumer

# Prometheus metrics
WORKER_TASKS_TOTAL = Counter(
    "worker_tasks_total", "Total tasks processed by the worker"
)
WORKER_ERRORS_TOTAL = Counter("worker_errors_total", "Total errors in worker tasks")



sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0,
    sample_rate=0.1,
    environment=os.getenv("ENV", "production"),
    send_default_pii=True,
)


async def main():
    print("🚀 Worker starting up", flush=True)

    threading.Thread(target=start_metrics_server, daemon=True).start()

    tasks = [
        asyncio.create_task(run_analysis_consumer()),
        asyncio.create_task(run_autotrade_consumer()),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            WORKER_ERRORS_TOTAL.inc()
            print(f"⚠️ Consumer task failed: {result}", flush=True)
        else:
            WORKER_TASKS_TOTAL.inc()


if __name__ == "__main__":
    asyncio.run(main())
