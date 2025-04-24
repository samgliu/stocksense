import json
import logging
import os

from aiokafka import AIOKafkaProducer

logger = logging.getLogger("stocksense")

USE_KAFKA = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
DB_POLL_INTERVAL_SECONDS = 5

producer = None


async def get_producer():
    global producer
    if producer is None and USE_KAFKA and KAFKA_BROKER:
        try:
            producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)
            await producer.start()
        except Exception as e:
            logger.warning(f"⚠️ Kafka producer init failed: {e}")
            producer = None
    return producer


async def send_kafka_msg(topic: str, event: dict, key: str = None):
    prod = await get_producer()
    if not prod:
        logger.warning("⚠️ Kafka producer not available.")
        return
    try:
        await prod.send_and_wait(topic, json.dumps(event).encode("utf-8"), key=key.encode("utf-8") if key else None)
    except Exception as e:
        logger.error(f"❌ Failed to send Kafka message: {e}")


async def stop_producer():
    global producer
    if producer:
        await producer.stop()
        producer = None
