import asyncio
import logging
import os
import time

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
        retry_backoff_ms=3000,
        metadata_max_age_ms=60000,
        request_timeout_ms=60000,
        session_timeout_ms=45000,
    )

    retries = 0
    last_error_time = 0
    error_cooldown_seconds = 300

    while max_retries is None or retries <= max_retries:
        try:
            await consumer.start()
            logger.info(f"Kafka consumer for topic '{topic}' started successfully.")
            return consumer
        except (KafkaConnectionError, NodeNotReadyError) as e:
            retries += 1
            now = time.time()

            if now - last_error_time > error_cooldown_seconds:
                last_error_time = now
                logger.error(f"Kafka connection failed (attempt {retries}/{max_retries}): {e}")
            else:
                logger.debug(f"Suppressed Kafka connection error (attempt {retries}/{max_retries}): {e}")

            if max_retries is not None and retries > max_retries:
                logger.error(f"Failed to start Kafka consumer after {max_retries} retries.")
                try:
                    await consumer.stop()
                except Exception as close_err:
                    logger.warning(f"Error stopping Kafka consumer: {close_err}")
                raise

            wait_time = min(30, 2**retries)
            await asyncio.sleep(wait_time)


async def commit_kafka(consumer, msg):
    if consumer and msg:
        tp = TopicPartition(msg.topic, msg.partition)
        await consumer.commit({tp: msg.offset + 1})
        await asyncio.sleep(0.5)
