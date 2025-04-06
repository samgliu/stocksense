import os
import json
from confluent_kafka import Producer
from app.services.redis import redis_client

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "invalid-broker-url")

producer = None
if KAFKA_ENABLED and KAFKA_BROKER:
    try:
        producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    except Exception as e:
        print(f"⚠️ Kafka initialization failed: {e}")
        producer = None


async def send_analysis_job_redis(data: dict, queue: str = "analysis-queue"):
    try:
        await redis_client.lpush(queue, json.dumps(data))
    except Exception as e:
        print(f"❌ Redis push failed: {e}")


async def send_analysis_job_kafka(data: dict, topic: str = "analysis-queue"):
    if not producer:
        print("⚠️ Kafka is not available.")
        return
    try:
        producer.produce(topic, value=json.dumps(data))
        producer.flush()
    except Exception as e:
        print(f"❌ Kafka produce failed: {e}")


async def send_analysis_job(data: dict, topic: str = "analysis-queue"):
    if KAFKA_ENABLED and producer:
        await send_analysis_job_kafka(data, topic)
    else:
        await send_analysis_job_redis(data, topic)
