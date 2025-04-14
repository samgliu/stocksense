import asyncio
import os
import json
from sqlalchemy import text
from app.database import AsyncSessionLocal
from confluent_kafka import Consumer as KafkaConsumer

USE_KAFKA = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
DB_POLL_INTERVAL_SECONDS = 5


def create_kafka_consumer(topic: str, group_id: str):
    if not (USE_KAFKA and KAFKA_BROKER):
        return None

    consumer = KafkaConsumer(
        {
            "bootstrap.servers": KAFKA_BROKER,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topic])
    return consumer


async def poll_kafka_msg(consumer):
    try:
        msg = consumer.poll(5.0)
        if msg and not msg.error():
            return json.loads(msg.value()), msg
        elif msg and msg.error():
            print(f"❌ Kafka poll error: {msg.error()}")
    except Exception as e:
        print(f"❌ Kafka poll exception: {e}")
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
        print(f"❌ DB poll failed: {e}")
        return None, None


def commit_kafka(consumer, msg):
    if consumer and msg:
        consumer.commit(msg)
