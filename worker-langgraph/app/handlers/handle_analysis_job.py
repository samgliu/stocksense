import json
from asyncio import sleep
from datetime import datetime, timezone
from logging import getLogger

from app.agents.analyzer_agent import run_analysis_graph
from app.database import AsyncSessionLocal
from app.models import JobStatus, StockEntry
from app.schemas.company import AnalyzeRequest
from app.utils.aws_lambda import invoke_gcs_lambda, invoke_scraper_lambda
from app.utils.message_queue import commit_kafka
from app.utils.redis import redis_client
from app.utils.sentiment_analysis import analyze_sentiment_with_cf
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = getLogger("stocksense")


async def wait_for_job(db: AsyncSession, job_id: str, retries: int = 5, delay: float = 0.3):
    for _ in range(retries):
        result = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
        job = result.scalar_one_or_none()
        if job:
            return job
        await sleep(delay)
    return None


async def handle_analysis_job(data: dict, msg, consumer=None):
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

            raw_input = data["body"]
            if isinstance(raw_input, str):
                try:
                    raw_input = json.loads(raw_input)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to decode job input: {e}")
                    return

            payload = AnalyzeRequest(**raw_input)
            # Scrape domain if available
            domain = payload.company.website
            scraped_text = ""
            if domain:
                try:
                    cleaned_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
                    scraped_text = invoke_scraper_lambda(cleaned_domain)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to scrape website {domain}: {e}")
            # Get GCS data
            gcs_snippets = []
            try:
                gcs_snippets = invoke_gcs_lambda(payload.company.name)
                logger.info(f"✅ GCS results for {payload.company.name}: {len(gcs_snippets)} items")
            except Exception as e:
                logger.warning(f"⚠️ Failed to retrieve GCS sentiment for {payload.company.name}: {e}")
            sentiment_analysis = None
            if gcs_snippets:
                try:
                    sentiment_analysis = await analyze_sentiment_with_cf(gcs_snippets)
                    logger.info(f"✅ sentiment analysis generated (length: {len(sentiment_analysis)} chars)")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate sentiment analysis: {e}")
            result = await run_analysis_graph(
                {
                    **payload.model_dump(),
                    "scraped_text": scraped_text,
                    "sentiment_analysis": sentiment_analysis,
                }
            )
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
                "analysis_report_id": (str(job.analysis_report_id) if job.analysis_report_id else None),
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

            await redis_client.set(f"job:{job_id}:status", json.dumps(job_status_data), ex=3600)
            logger.info(f"✅ Job {job_id} done and committed")

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error processing job {data.get('job_id')}: {e}")
        finally:
            if consumer and msg:
                await commit_kafka(consumer, msg)
