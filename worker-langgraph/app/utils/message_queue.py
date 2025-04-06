# app/services/message_queue.py

import os
import json
import asyncio
from confluent_kafka import Consumer as KafkaConsumer
from app.utils.redis import redis_client

USE_KAFKA = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
KAFKA_TOPIC = "analysis-queue"

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
    print("📦 Redis consumer mode enabled")


# POLL MESSAGE
async def poll_next():
    if consumer is not None:
        try:
            msg = consumer.poll(1.0)
            if msg and not msg.error():
                return json.loads(msg.value()), msg
            elif msg and msg.error():
                print(f"❌ Kafka poll error: {msg.error()}")
        except Exception as e:
            print(f"❌ Kafka poll exception: {e}")
        return None, None

    # Redis fallback
    try:
        data = await redis_client.rpop(KAFKA_TOPIC)
        if data:
            return json.loads(data), None
    except Exception as e:
        print(f"❌ Redis JSON decode error: {e}")
    return None, None


# COMMIT OFFSET
def commit(msg):
    if consumer and msg:
        consumer.commit(msg)
