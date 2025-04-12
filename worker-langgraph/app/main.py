from app.utils.message_queue import (
    create_kafka_consumer,
    poll_from_kafka,
    poll_from_db,
    commit_kafka,
)
from app.agents.analyzer import handle_analysis_job


async def main():
    print("🚀 Worker started", flush=True)

    consumer = create_kafka_consumer()

    while True:
        data, msg = None, None

        if consumer:
            data, msg = await poll_from_kafka(consumer)
        else:
            data, msg = await poll_from_db()

        if not data:
            continue  # No job

        print(f"📥 Received job: {data.get('job_id')}", flush=True)

        await handle_analysis_job(data, msg, consumer)

        if msg and consumer:
            commit_kafka(consumer, msg)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
