import asyncio
from app.consumers.analysis_consumer import run_analysis_consumer
from app.consumers.autotrade_consumer import run_autotrade_consumer


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
