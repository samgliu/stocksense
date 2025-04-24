import asyncio
import json
import logging
import os

from aiokafka import AIOKafkaConsumer, TopicPartition

logger = logging.getLogger("stocksense")

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")


async def create_kafka_consumer(topic: str, group_id: str):
    if not (KAFKA_ENABLED and KAFKA_BROKER):
        return None
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        group_id=group_id,
        auto_offset_reset="latest",
        enable_auto_commit=False,
    )
    await consumer.start()
    return consumer


async def poll_kafka_msg(consumer):
    try:
        async for msg in consumer:
            if msg.value:
                data = json.loads(msg.value)
                return data, msg
    except Exception as e:
        logger.error(f"Kafka message poll error: {e}")
    return None, None


async def commit_kafka(consumer, msg):
    if consumer and msg:
        tp = TopicPartition(msg.topic, msg.partition)
        await consumer.commit({tp: msg.offset + 1})
        await asyncio.sleep(0.5)
