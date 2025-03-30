from confluent_kafka import Producer
import json

producer = Producer({"bootstrap.servers": "kafka:9092"})


def send_analysis_job(data: dict, topic: str = "analysis-queue"):
    producer.produce(topic, value=json.dumps(data))
    producer.flush()
