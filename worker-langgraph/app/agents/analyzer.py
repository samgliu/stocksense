import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import JobStatus, StockEntry
from app.schemas.company import AnalyzeRequest
from app.agents.analyzer_agent import run_analysis_graph
from app.utils.redis import redis_client
from app.utils.message_queue import poll_next, commit
from asyncio import sleep


async def wait_for_job(
    db: AsyncSession, job_id: str, retries: int = 5, delay: float = 0.3
):
    for _ in range(retries):
        result = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
        job = result.scalar_one_or_none()
        if job:
            return job
        await sleep(delay)
    return None


async def handle_analysis_job(data: dict, msg):
    async with AsyncSessionLocal() as db:
        try:
            job_id = data["job_id"]
            user_id = data["user_id"]
            print(f"⚙️  Processing job {job_id} for user {data['email']}...")
            job = await wait_for_job(db, job_id)
            if not job:
                print(f"❌ Job {job_id} not found after retries")
                commit(msg)
                return
            job.status = "processing"
            await db.commit()
            await db.flush()

            raw_input = data["body"]
            if isinstance(raw_input, str):
                try:
                    raw_input = json.loads(raw_input)
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to decode job input: {e}")
                    return

            payload = AnalyzeRequest(**raw_input)
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

            db.add(
                StockEntry(
                    user_id=user_id,
                    text_input=payload.company.ticker,
                    summary=summary,
                    source_type="company",
                    model_used="gemini",
                )
            )
            await db.commit()
            commit(msg)
            await redis_client.set(
                f"job:{job_id}:status", json.dumps(job_status_data), ex=3600
            )
            print(f"✅ Job {job_id} done and committed")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error processing job {data.get('job_id')}: {e}")
        finally:
            if msg:
                commit(msg)
