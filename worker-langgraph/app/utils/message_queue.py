import asyncio
import json
import logging
import os

from app.database import AsyncSessionLocal
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import text

logger = logging.getLogger("stocksense")

USE_KAFKA = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
DB_POLL_INTERVAL_SECONDS = 5


async def create_kafka_consumer(topic: str, group_id: str):
    if not (USE_KAFKA and KAFKA_BROKER):
        return None
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    return consumer


async def poll_kafka_msg(consumer):
    try:
        async for msg in consumer:
            if msg.value:
                return json.loads(msg.value), msg
    except Exception as e:
        logger.error(f"❌ Kafka poll exception: {e}")
    return None, None


async def poll_analysis_job_from_db():
    """Fallback for analysis jobs only."""
    await asyncio.sleep(DB_POLL_INTERVAL_SECONDS)
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text(
                    """
                    SELECT * FROM job_status
                    WHERE status = 'queued'
                    ORDER BY created_at
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                """
                )
            )
            row = result.mappings().fetchone()
            if row is None:
                return None, None

            await db.execute(
                text(
                    """
                    UPDATE job_status
                    SET status = 'processing', updated_at = NOW()
                    WHERE id = :id
                """
                ),
                {"id": row.id},
            )
            await db.commit()

            return {
                "job_id": row.job_id,
                "user_id": str(row.user_id),
                "email": "",
                "body": row.input,
            }, None
    except Exception as e:
        logger.error(f"❌ DB poll failed: {e}")
        return None, None


async def commit_kafka(consumer, msg):
    if consumer and msg:
        await consumer.commit()
