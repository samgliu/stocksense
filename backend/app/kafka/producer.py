import os
import json
from confluent_kafka import Producer

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
        print(f"📤 Job sent to Kafka topic '{topic}'")
    except Exception as e:
        print(f"❌ Kafka produce failed: {e}")


async def send_analysis_job(data: dict, stream: str = "analysis-queue"):
    if KAFKA_ENABLED and producer:
        await send_analysis_job_kafka(data, topic=stream)
    else:
        print("📝 Kafka disabled; job already inserted in DB.")


async def send_autotrade_job(data: dict):
    await send_analysis_job(data, stream="autotrade.jobs")
