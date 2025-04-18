from app.utils.message_queue import (
    create_kafka_consumer,
    poll_kafka_msg,
    commit_kafka,
    poll_analysis_job_from_db,
)
from app.handlers.handle_analysis_job import handle_analysis_job
import asyncio
import sentry_sdk
import time


async def run_analysis_consumer():
    print("🚀 Starting analysis consumer", flush=True)

    consumer = create_kafka_consumer("analysis-queue", "langgraph-consumer")

    if consumer:
        print("✅ Kafka consumer initialized for 'analysis-queue'", flush=True)
    else:
        print(
            "⚠️ Kafka disabled or failed to initialize — falling back to DB polling",
            flush=True,
        )

    last_sentry_report = 0
    SENTRY_THROTTLE_SECONDS = 300

    while True:
        try:
            if consumer:
                data, msg = await poll_kafka_msg(consumer)
            else:
                data, msg = await poll_analysis_job_from_db()

            if not data:
                await asyncio.sleep(1)
                continue

            print(f"📥 Job received: {data.get('job_id')}", flush=True)

            await handle_analysis_job(data, msg, consumer)

            if msg and consumer:
                print("✅ Committing Kafka offset...", flush=True)
                commit_kafka(consumer, msg)

        except Exception as e:
            print(f"❌ Error in analysis consumer loop: {e}", flush=True)
            now = time.time()
            if now - last_sentry_report > SENTRY_THROTTLE_SECONDS:
                sentry_sdk.capture_exception(e)
                last_sentry_report = now
            await asyncio.sleep(1)
