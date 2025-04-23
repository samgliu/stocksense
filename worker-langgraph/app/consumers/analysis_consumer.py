import asyncio
import logging
import time
import json

import sentry_sdk
from app.handlers.handle_analysis_job import handle_analysis_job
from app.utils.message_queue import (
    commit_kafka,
    create_kafka_consumer,
    poll_analysis_job_from_db,
)

logger = logging.getLogger("stocksense")


async def run_analysis_consumer():
    logger.info("🚀 Starting analysis consumer")

    consumer = await create_kafka_consumer("analysis-queue", "langgraph-consumer")

    if consumer:
        logger.info("✅ Kafka consumer initialized for 'analysis-queue'")
        last_sentry_report = 0
        SENTRY_THROTTLE_SECONDS = 300
        try:
            async for msg in consumer:
                try:
                    if msg.value:
                        data = json.loads(msg.value)
                        logger.info(f"📥 Job received: {data.get('job_id')}")
                        await handle_analysis_job(data, msg, consumer)
                        logger.info("✅ Committing Kafka offset...")
                        await commit_kafka(consumer, msg)
                except Exception as e:
                    logger.error(f"❌ Error processing analysis job: {e}")
                    now = time.time()
                    if now - last_sentry_report > SENTRY_THROTTLE_SECONDS:
                        sentry_sdk.capture_exception(e)
                        last_sentry_report = now
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"❌ Error in analysis consumer loop: {e}")
            now = time.time()
            if now - last_sentry_report > SENTRY_THROTTLE_SECONDS:
                sentry_sdk.capture_exception(e)
                last_sentry_report = now
            await asyncio.sleep(1)
        finally:
            await consumer.stop()
    else:
        logger.warning("⚠️ Kafka disabled or failed to initialize — falling back to DB polling")
        while True:
            data = await poll_analysis_job_from_db()
            if data:
                await handle_analysis_job(data, None, None)
            await asyncio.sleep(1)
