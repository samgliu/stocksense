import asyncio
from app.utils.message_queue import get_consumer, poll_next, commit
from app.agents.analyzer import handle_analysis_job


async def main():
    print("🚀 Worker started", flush=True)

    consumer = get_consumer()
    if not consumer:
        print("❌ Kafka consumer not initialized. Exiting.")
        return

    while True:
        data, msg = await poll_next(consumer)

        if not data:
            await asyncio.sleep(0.5)
            continue

        print(f"📥 Received job: {data.get('job_id')}", flush=True)

        await handle_analysis_job(data, msg)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
