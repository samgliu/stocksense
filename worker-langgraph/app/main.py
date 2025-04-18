import asyncio
from app.consumers.analysis_consumer import run_analysis_consumer
from app.consumers.autotrade_consumer import run_autotrade_consumer
import sentry_sdk
import os

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0,
    sample_rate=0.1,
    environment=os.getenv("ENV", "production"),
    send_default_pii=True,
)

async def main():
    print("🚀 Worker starting up", flush=True)

    tasks = [
        asyncio.create_task(run_analysis_consumer()),
        asyncio.create_task(run_autotrade_consumer()),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"⚠️ Consumer task failed: {result}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
