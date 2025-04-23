import json
import logging
from asyncio import sleep
from datetime import datetime, timezone

from app.agents.analyzer_stream_agent import run_analysis_graph_stream
from app.database import AsyncSessionLocal
from app.models.job_status import JobStatus
from app.models.stock_entry import StockEntry
from app.utils.message_queue import commit_kafka
from app.utils.redis import redis_client
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("stocksense")


async def wait_for_job(db: AsyncSession, job_id: str, retries: int = 5, delay: float = 0.3):
    for _ in range(retries):
        result = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
        job = result.scalar_one_or_none()
        if job:
            return job
        await sleep(delay)
    return None


async def handle_analysis_stream_job(data: dict, msg, consumer=None):
    if data.get("node") is not None:
        return
    async with AsyncSessionLocal() as db:
        try:
            job_id = data["job_id"]
            user_id = data["user_id"]
            logger.info(f"⚙️  Processing job {job_id} for user {data['email']}...")
            job = await wait_for_job(db, job_id)
            if not job:
                logger.error(f"❌ Job {job_id} not found after retries")
                return

            job.status = "processing"
            await db.commit()
            await db.flush()

            result = None
            async for r in run_analysis_graph_stream(data):
                result = r
            if result is None:
                logger.error(f"❌ No result from run_analysis_graph_stream for job {job_id}")
                return
            summary = result["analyze"]
            job.status = "done"
            job.result = json.dumps(summary)
            job.updated_at = datetime.now(timezone.utc)
            await db.flush()

            job_status_data = {
                "job_id": job_id,
                "status": job.status,
                "result": job.result,
                "updated_at": job.updated_at.isoformat(),
                "analysis_report_id": (str(job.analysis_report_id) if job.analysis_report_id else None),
            }

            db.add(
                StockEntry(
                    user_id=user_id,
                    text_input=result["analyze"]["payload"]["company"]["ticker"],
                    summary=json.dumps(summary),
                    source_type="company",
                    model_used="gemini",
                )
            )
            await db.commit()

            await redis_client.set(f"job:{job_id}:status", json.dumps(job_status_data), ex=3600)
            logger.info(f"✅ Job {job_id} done and committed")

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error processing job {data.get('job_id')}: {e}")
        finally:
            if consumer and msg:
                await commit_kafka(consumer, msg)
