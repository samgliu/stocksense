import asyncio
import json
import os
from datetime import datetime, timezone

from confluent_kafka import Consumer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, AsyncSessionLocal
from app.models import JobStatus, StockEntry, UsageLog
from app.schemas.company import AnalyzeRequest
from app.langgraph_app import run_analysis_graph
from app.utils.redis import redis_client

# Config
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = "analysis-queue"

# Kafka config
consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "langgraph-consumer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
)

consumer.subscribe([KAFKA_TOPIC])
print(f"🚀 LangGraph worker is listening to '{KAFKA_TOPIC}'...")


async def handle_message(data: dict, msg):
    async with AsyncSessionLocal() as db:
        try:
            job_id = data["job_id"]
            user_id = data["user_id"]
            payload = AnalyzeRequest(**data["body"])

            print(f"⚙️  Processing job {job_id} for user {data['email']}...")
            job = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
            job = job.scalar_one()
            job.status = "processing"
            await db.flush()

            result = await run_analysis_graph(payload.model_dump())
            summary = result["result"]

            job.status = "done"
            job.result = summary
            job.updated_at = datetime.now(timezone.utc)
            await db.flush()

            job_status_data = {
                "job_id": job_id,
                "status": job.status,
                "result": job.result,
                "updated_at": job.updated_at.isoformat(),
                "analysis_report_id": (
                    str(job.analysis_report_id) if job.analysis_report_id else None
                ),
            }

            await redis_client.set(
                f"job:{job_id}:status", json.dumps(job_status_data), ex=3600
            )

            db.add(
                StockEntry(
                    user_id=user_id,
                    text_input=payload.company.ticker,
                    summary=summary,
                    source_type="company",
                    model_used="gemini",
                )
            )
            db.add(UsageLog(user_id=user_id, action="analyze"))
            await db.commit()

            consumer.commit(msg)
            print(f"✅ Job {job_id} done and committed to Kafka")

        except Exception as e:
            print(f"❌ Error processing job {data.get('job_id')}: {e}")


async def consume_loop():
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            await asyncio.sleep(0.1)
            continue

        if msg.error():
            print("❌ Kafka error:", msg.error())
            continue

        try:
            data = json.loads(msg.value())
            asyncio.create_task(handle_message(data, msg))
        except Exception as e:
            print(f"❌ JSON decode error: {e}")


if __name__ == "__main__":
    asyncio.run(consume_loop())
