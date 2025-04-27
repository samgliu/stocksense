import asyncio
import logging
import os
import time

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.errors import KafkaConnectionError, NodeNotReadyError
from app.database import AsyncSessionLocal
from sqlalchemy import text

logger = logging.getLogger("stocksense")

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
DB_POLL_INTERVAL_SECONDS = 5


async def create_kafka_consumer(topic: str, group_id: str, max_retries: int = 5):
    if not (KAFKA_ENABLED and KAFKA_BROKER):
        return None

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        group_id=group_id,
        auto_offset_reset="latest",
        enable_auto_commit=False,
        retry_backoff_ms=1000,
        request_timeout_ms=60000,
        session_timeout_ms=45000,
    )

    retries = 0
    last_error_time = 0
    error_cooldown_seconds = 300

    while max_retries is None or retries <= max_retries:
        try:
            await consumer.start()
            logger.info(f"Kafka consumer for topic '{topic}' started successfully.")
            return consumer
        except (KafkaConnectionError, NodeNotReadyError) as e:
            retries += 1
            now = time.time()

            if now - last_error_time > error_cooldown_seconds:
                last_error_time = now
                logger.error(f"Kafka connection failed (attempt {retries}/{max_retries}): {e}")
            else:
                logger.debug(f"Suppressed Kafka connection error (attempt {retries}/{max_retries}): {e}")

            if max_retries is not None and retries > max_retries:
                logger.error(f"Failed to start Kafka consumer after {max_retries} retries.")
                raise

            wait_time = 2**retries  # 2s, 4s, 8s, etc.
            await asyncio.sleep(wait_time)


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
        tp = TopicPartition(msg.topic, msg.partition)
        await consumer.commit({tp: msg.offset + 1})
        await asyncio.sleep(0.5)
