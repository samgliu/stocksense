import asyncio
import os
import json
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.models import JobStatus
from confluent_kafka import Consumer as KafkaConsumer

USE_KAFKA = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
KAFKA_TOPIC = "analysis-queue"
DB_POLL_INTERVAL_SECONDS = 5

consumer = None

if USE_KAFKA and KAFKA_BROKER:
    try:
        consumer = KafkaConsumer(
            {
                "bootstrap.servers": KAFKA_BROKER,
                "group.id": "langgraph-consumer",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )
        consumer.subscribe([KAFKA_TOPIC])
        print(f"✅ Kafka consumer initialized on topic '{KAFKA_TOPIC}'")
    except Exception as e:
        print(f"⚠️ Kafka consumer failed: {e}")
        consumer = None
else:
    print("📦 Kafka disabled; using DB fallback polling")


# POLL MESSAGE
async def poll_next():
    if consumer:
        try:
            msg = consumer.poll(1.0)
            if msg and not msg.error():
                return json.loads(msg.value()), msg
            elif msg and msg.error():
                print(f"❌ Kafka poll error: {msg.error()}")
        except Exception as e:
            print(f"❌ Kafka poll exception: {e}")
        return None, None

    # DB fallback using FOR UPDATE SKIP LOCKED
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

            # Mark as processing
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


# COMMIT OFFSET
def commit(msg):
    if consumer and msg:
        consumer.commit(msg)
