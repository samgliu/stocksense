import asyncio
import logging
import time
import json

import sentry_sdk
from app.handlers.handle_autotrade_job import handle_autotrade_job
from app.utils.message_queue import commit_kafka, create_kafka_consumer

logger = logging.getLogger("stocksense")


async def run_autotrade_consumer():
    logger.info("🚀 Starting AutoTrader consumer")

    consumer = await create_kafka_consumer("autotrade.jobs", "autotrade-consumer")

    if consumer:
        logger.info("✅ Kafka consumer initialized for 'autotrade.jobs'")
        last_sentry_report = 0
        SENTRY_THROTTLE_SECONDS = 300
        try:
            async for msg in consumer:
                try:
                    if msg.value:
                        data = json.loads(msg.value)
                        logger.info(f"📥 Received AutoTrader job: {data.get('job_id') or data.get('ticker')}")
                        await handle_autotrade_job(data)
                        logger.info("✅ Committing Kafka offset")
                        await commit_kafka(consumer, msg)
                except Exception as e:
                    logger.error(f"❌ Error processing AutoTrader job: {e}")
                    now = time.time()
                    if now - last_sentry_report > SENTRY_THROTTLE_SECONDS:
                        sentry_sdk.capture_exception(e)
                        last_sentry_report = now
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"❌ Error in AutoTrader consumer loop: {e}")
            now = time.time()
            if now - last_sentry_report > SENTRY_THROTTLE_SECONDS:
                sentry_sdk.capture_exception(e)
                last_sentry_report = now
            await asyncio.sleep(1)
        finally:
            await consumer.stop()
    else:
        logger.error("❌ Kafka consumer failed to initialize")
        return
