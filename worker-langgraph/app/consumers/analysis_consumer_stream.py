import asyncio
import logging

from app.handlers.handle_analysis_stream_job import handle_analysis_stream_job
from app.utils.message_queue import commit_kafka, create_kafka_consumer, poll_kafka_msg

logger = logging.getLogger("stocksense")


async def run_analysis_consumer_stream():
    logger.info("🚀 Starting streaming analysis consumer")
    consumer = await create_kafka_consumer("analysis-stream-queue", "analysis-consumer-group")

    if not consumer:
        logger.info("⚠️ Kafka disabled or failed to initialize — streaming consumer will not run")
        return

    logger.info("✅ Kafka consumer initialized for 'analysis-stream-queue'")

    try:
        async for msg in consumer:
            try:
                if msg.value:
                    import json
                    data = json.loads(msg.value)
                    logger.info(f"📥 Stream job received: {data.get('job_id')}")
                    await handle_analysis_stream_job(data, msg, consumer)
                    logger.info("✅ Committing Kafka offset...")
                    await commit_kafka(consumer, msg)
            except Exception as e:
                import traceback
                logger.info(f"❌ Exception in streaming analysis consumer: {e}\n{traceback.format_exc()}")
                await asyncio.sleep(1)
    finally:
        await consumer.stop()
