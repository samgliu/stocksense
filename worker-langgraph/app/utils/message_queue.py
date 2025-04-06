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

REDIS_STREAM = "analysis-stream"
REDIS_CONSUMER_GROUP = "worker-group"
REDIS_CONSUMER_NAME = "worker-1"


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

    # Redis Stream fallback (Kafka disabled)
    try:
        # Create group if not exists
        try:
            await redis_client.xgroup_create(
                REDIS_STREAM, REDIS_CONSUMER_GROUP, id="0", mkstream=True
            )
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                print(f"⚠️ Redis stream group creation failed: {e}")

        entries = await redis_client.xreadgroup(
            groupname=REDIS_CONSUMER_GROUP,
            consumername=REDIS_CONSUMER_NAME,
            streams={REDIS_STREAM: ">"},
            count=1,
            block=5000,  # ms (5s)
        )

        if entries:
            stream_key, messages = entries[0]
            msg_id, msg_data = messages[0]
            payload = json.loads(msg_data["payload"])
            return payload, (REDIS_STREAM, msg_id)

        return None, None  # timeout reached, nothing to do

    except Exception as e:
        print(f"❌ Redis stream read error: {e}")
        return None, None


# COMMIT OFFSET
def commit(msg):
    if consumer and msg:
        consumer.commit(msg)
    elif isinstance(msg, tuple) and len(msg) == 2:
        stream_name, msg_id = msg
        try:
            asyncio.create_task(
                redis_client.xack(stream_name, REDIS_CONSUMER_GROUP, msg_id)
            )
        except Exception as e:
            print(f"❌ Redis stream ack failed: {e}")
