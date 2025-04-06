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


async def send_analysis_job_kafka(data: dict, topic: str = "analysis-queue"):
    if not producer:
        print("⚠️ Kafka is not available.")
        return
    try:
        producer.produce(topic, value=json.dumps(data))
        producer.flush()
    except Exception as e:
        print(f"❌ Kafka produce failed: {e}")


async def send_analysis_job_stream(data: dict, stream: str = "analysis-stream"):
    try:
        await redis_client.xadd(stream, {"payload": json.dumps(data)})
        print(f"📤 Job sent to Redis stream '{stream}'")
    except Exception as e:
        print(f"❌ Redis stream push failed: {e}")


async def send_analysis_job(data: dict, stream: str = "analysis-stream"):
    if KAFKA_ENABLED and producer:
        await send_analysis_job_kafka(data, topic=stream)
    else:
        await send_analysis_job_stream(data, stream=stream)
