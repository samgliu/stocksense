import json
import logging
from asyncio import sleep
from datetime import datetime, timezone

from app.agents.analyzer_stream_agent import run_analysis_graph_stream
from app.database import AsyncSessionLocal
from app.models.analysis_report import AnalysisReport
from app.models.job_status import JobStatus
from app.models.stock_entry import StockEntry
from app.utils.message_queue import commit_kafka
from app.utils.redis import redis_client
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("stocksense")


async def persist_analysis_report(job: JobStatus, db: AsyncSession) -> None:
    if job.status != "done" or not job.result:
        return
    try:
        parsed_result = json.loads(job.result)
        result_str = parsed_result.get("result", "{}")
        result = json.loads(result_str)
        prediction = result.get("prediction", {})
        insights = result.get("insights")
        payload = parsed_result.get("payload", {})
        company_info = payload.get("company", {})
        company_id = payload.get("company_id")
        ticker = company_info.get("ticker")
        exchange = company_info.get("exchange")
        current_price = company_info.get("current_price")
        report = AnalysisReport(
            company_id=company_id,
            ticker=ticker,
            exchange=exchange,
            model_version="gemini",
            current_price=current_price,
            min_price=prediction.get("min"),
            max_price=prediction.get("max"),
            avg_price=prediction.get("average"),
            time_horizon=prediction.get("time_horizon", "30d"),
            prediction_json=prediction,
            insights=insights,
        )
        db.add(report)
        await db.flush()
        job.analysis_report_id = report.id
    except Exception as e:
        await db.rollback()
        logger.exception(f"❌ Failed to persist report: {e}")


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

            job = await wait_for_job(db, job_id)
            if not job:
                logger.error(f"❌ Job {job_id} not found after retries")
                return

            job.status = "processing"
            await db.commit()

            final_output = None
            async for step in run_analysis_graph_stream(data):
                if isinstance(step, dict) and len(step) == 1:
                    node_name, output = next(iter(step.items()))
                    if node_name == "analyze":
                        final_output = output

            if not final_output:
                logger.error(f"❌ No final result from run_analysis_graph_stream for job {job_id}")
                return

            job.status = "done"
            job.result = json.dumps(final_output)
            job.updated_at = datetime.now(timezone.utc)
            await db.flush()
            await persist_analysis_report(job, db)
            await db.refresh(job)

            payload = json.loads(job.result).get("payload", {}) if job.result else {}
            company_info = payload.get("company", {})
            ticker = company_info.get("ticker")
            company_id = payload.get("company_id")
            try:
                result = json.loads(job.result)
                summary = result.get("result", {})
            except Exception:
                return

            db.add(
                StockEntry(
                    user_id=job.user_id,
                    company_id=company_id,
                    text_input=ticker,
                    summary=summary,
                    source_type="company",
                    model_used="gemini",
                )
            )

            updated_at = job.updated_at
            analysis_report_id = job.analysis_report_id
            await db.commit()

            job_status_data = {
                "job_id": job_id,
                "status": job.status,
                "updated_at": updated_at.isoformat() if updated_at else None,
                "analysis_report_id": str(analysis_report_id) if analysis_report_id else None,
            }
            await redis_client.set(f"job:{job_id}:status", json.dumps(job_status_data), ex=3600)

            if consumer and msg:
                await commit_kafka(consumer, msg)

            logger.info(f"✅ Job {job_id} processed and committed.")

        except Exception as e:
            await db.rollback()
            logger.exception(f"❌ Error processing job {data.get('job_id')}: {e}")
