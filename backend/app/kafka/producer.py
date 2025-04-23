import json
import logging
import os

from aiokafka import AIOKafkaProducer

logger = logging.getLogger("stocksense")

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "invalid-broker-url")

producer = None

async def get_producer():
    global producer
    if producer is None and KAFKA_ENABLED and KAFKA_BROKER:
        try:
            producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)
            await producer.start()
        except Exception as e:
            logger.warning(f"⚠️ Kafka initialization failed: {e}")
            producer = None
    return producer


async def send_analysis_job_kafka(data: dict, topic: str = "analysis-queue"):
    prod = await get_producer()
    if not prod:
        logger.warning("⚠️ Kafka is not available.")
        return
    try:
        await prod.send_and_wait(topic, json.dumps(data).encode("utf-8"))
        logger.info(f"📤 Job sent to Kafka topic '{topic}'")
    except Exception as e:
        logger.error(f"❌ Kafka produce failed: {e}")


async def send_analysis_job(data: dict, stream: str = "analysis-queue"):
    prod = await get_producer()
    if KAFKA_ENABLED and prod:
        await send_analysis_job_kafka(data, topic=stream)
    else:
        logger.info("📝 Kafka disabled; job already inserted in DB.")


async def send_autotrade_job(data: dict):
    await send_analysis_job(data, stream="autotrade.jobs")
