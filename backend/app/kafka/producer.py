import os
from confluent_kafka import Producer
import json

KAFKA_BROKER = os.getenv("KAFKA_BROKER")
producer = Producer({"bootstrap.servers": KAFKA_BROKER})


def send_analysis_job(data: dict, topic: str = "analysis-queue"):
    producer.produce(topic, value=json.dumps(data))
    producer.flush()
