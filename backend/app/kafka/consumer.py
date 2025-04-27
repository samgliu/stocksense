import asyncio
import json
import logging
import os

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.errors import KafkaConnectionError, NodeNotReadyError

logger = logging.getLogger("stocksense")

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")


async def create_kafka_consumer(topic: str, group_id: str, max_retries: int = 5):
    if not (KAFKA_ENABLED and KAFKA_BROKER):
        return None

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        group_id=group_id,
        auto_offset_reset="latest",
        enable_auto_commit=False,
    )

    retries = 0
    while retries <= max_retries:
        try:
            await consumer.start()
            print(f"Kafka consumer for topic '{topic}' started successfully.")
            return consumer
        except (KafkaConnectionError, NodeNotReadyError) as e:
            retries += 1
            if retries > max_retries:
                print(f"Failed to start Kafka consumer after {max_retries} retries.")
                raise
            wait_time = 2**retries  # exponential backoff: 2s, 4s, 8s, 16s, etc.
            print(f"Kafka connection failed (attempt {retries}/{max_retries}): {e}. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)


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
